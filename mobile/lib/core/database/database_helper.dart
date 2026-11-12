import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as p;
import 'package:sqflite/sqflite.dart';
import '../../services/catalogo_service.dart';
import '../../services/carrito_service.dart';
import '../../services/reserva_service.dart';
import '../../services/pedido_service.dart';
import '../../services/devoluciones_service.dart';

class DatabaseHelper {
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  factory DatabaseHelper() => _instance;
  DatabaseHelper._internal();

  static Database? _database;

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  /// Permite inyectar una base de datos en pruebas (ej: ffi / in-memory).
  @visibleForTesting
  static void setMockDatabase(Database? db) {
    _database = db;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = p.join(dbPath, 'aurora_store_mobile.db');

    return await openDatabase(
      path,
      version: 3,
      onCreate: _onCreate,
      onUpgrade: _onUpgrade,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    // 1. Tiendas / Tenants almacenados localmente
    await db.execute('''
      CREATE TABLE local_tenants (
        id_empresa INTEGER PRIMARY KEY,
        nombre_empresa TEXT NOT NULL,
        slug TEXT,
        razon_social TEXT,
        logo TEXT,
        ciudad TEXT,
        direccion_fiscal TEXT,
        updated_at TEXT NOT NULL
      );
    ''');

    // 2. Catálogo de productos particionado por id_empresa
    await db.execute('''
      CREATE TABLE local_products (
        id_producto INTEGER NOT NULL,
        id_empresa INTEGER NOT NULL,
        id_categoria INTEGER,
        categoria_nombre TEXT,
        codigo_producto TEXT,
        nombre TEXT NOT NULL,
        descripcion TEXT,
        marca TEXT,
        genero TEXT,
        precio REAL NOT NULL,
        estado_stock TEXT,
        stock_disponible_catalogo INTEGER,
        imagen_principal TEXT,
        tiene_ra INTEGER DEFAULT 0,
        raw_json TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (id_producto, id_empresa)
      );
    ''');
    await db.execute('CREATE INDEX idx_products_empresa ON local_products (id_empresa);');
    await db.execute('CREATE INDEX idx_products_categoria ON local_products (id_empresa, id_categoria);');

    // 3. Detalles de productos en caché offline particionado por id_empresa
    await db.execute('''
      CREATE TABLE local_product_details (
        id_producto INTEGER NOT NULL,
        id_empresa INTEGER NOT NULL,
        raw_json TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (id_producto, id_empresa)
      );
    ''');

    // 4. Borrador local de carrito particionado por id_empresa e id_usuario
    await db.execute('''
      CREATE TABLE local_cart_drafts (
        id_empresa INTEGER NOT NULL,
        id_usuario INTEGER NOT NULL,
        id_variante INTEGER NOT NULL,
        id_producto INTEGER NOT NULL,
        producto_nombre TEXT NOT NULL,
        talla_nombre TEXT,
        color_nombre TEXT,
        codigo_hex TEXT,
        precio_unitario REAL NOT NULL,
        cantidad INTEGER NOT NULL,
        imagen_url TEXT,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (id_empresa, id_usuario, id_variante)
      );
    ''');

    // 5. Cola de operaciones pendientes de sincronización con UUID estable (POST /api/sync/lote)
    await db.execute('''
      CREATE TABLE local_sync_operations (
        operation_id TEXT PRIMARY KEY,
        id_empresa INTEGER NOT NULL,
        id_usuario INTEGER NOT NULL,
        id_sucursal INTEGER,
        kind TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        status TEXT NOT NULL,
        conflict_code TEXT,
        message TEXT,
        retry_count INTEGER DEFAULT 0,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
      );
    ''');
    await db.execute('CREATE INDEX idx_sync_status ON local_sync_operations (status);');
    await db.execute('CREATE INDEX idx_sync_user_empresa ON local_sync_operations (id_usuario, id_empresa);');

    // 6. Recibos durables de confirmación de sincronización
    await db.execute('''
      CREATE TABLE local_sync_receipts (
        operation_id TEXT PRIMARY KEY,
        id_empresa INTEGER NOT NULL,
        id_usuario INTEGER NOT NULL,
        response_json TEXT NOT NULL,
        created_at TEXT NOT NULL
      );
    ''');

    // 7. Reservas locales (incluyendo borradores offline)
    await db.execute('''
      CREATE TABLE local_reservations (
        id_reserva_local TEXT PRIMARY KEY,
        codigo_reserva TEXT,
        id_empresa INTEGER NOT NULL,
        id_usuario INTEGER NOT NULL,
        id_sucursal INTEGER,
        sucursal_nombre TEXT,
        fecha_hora_visita TEXT,
        items_json TEXT,
        observaciones TEXT,
        estado TEXT NOT NULL,
        is_offline_draft INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
      );
    ''');

    // 8. Devoluciones del cliente en caché local
    await db.execute('''
      CREATE TABLE local_devoluciones (
        id_devolucion INTEGER NOT NULL,
        id_empresa INTEGER NOT NULL,
        id_usuario INTEGER NOT NULL,
        id_venta INTEGER NOT NULL,
        codigo_venta TEXT,
        motivo TEXT NOT NULL,
        tipo_resolucion TEXT,
        estado TEXT NOT NULL,
        monto_reembolso REAL DEFAULT 0,
        items_json TEXT,
        created_at TEXT NOT NULL,
        PRIMARY KEY (id_devolucion, id_empresa)
      );
    ''');

    // 9. Filtros y categorías en caché local particionados por id_empresa
    await db.execute('''
      CREATE TABLE local_filtros (
        id_empresa INTEGER PRIMARY KEY,
        raw_json TEXT NOT NULL,
        updated_at TEXT NOT NULL
      );
    ''');

    // 10. Sucursales de tiendas particionadas por empresa para verificación y reservas offline
    await db.execute('''
      CREATE TABLE local_sucursales (
        id_sucursal INTEGER NOT NULL,
        id_empresa INTEGER NOT NULL,
        nombre TEXT NOT NULL,
        direccion TEXT,
        telefono TEXT,
        ciudad TEXT,
        raw_json TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        PRIMARY KEY (id_sucursal, id_empresa)
      );
    ''');

    // 11. Pedidos históricos del usuario en caché local
    await db.execute('''
      CREATE TABLE local_pedidos (
        id_pedido INTEGER NOT NULL,
        id_empresa INTEGER NOT NULL,
        id_usuario INTEGER NOT NULL,
        codigo_pedido TEXT NOT NULL,
        estado TEXT NOT NULL,
        raw_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        PRIMARY KEY (id_pedido, id_empresa, id_usuario)
      );
    ''');
    await db.execute('CREATE INDEX idx_pedidos_user ON local_pedidos (id_usuario, id_empresa);');

    // Auto-poblar datos canónicos iniciales para disponibilidad inmediata offline
    await _autoPoblarSucursalesIniciales(db);
    await _autoPoblarProductosIniciales(db);
  }

  Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
    if (oldVersion < 2) {
      await db.execute('''
        CREATE TABLE IF NOT EXISTS local_filtros (
          id_empresa INTEGER PRIMARY KEY,
          raw_json TEXT NOT NULL,
          updated_at TEXT NOT NULL
        );
      ''');
      await db.execute('''
        CREATE TABLE IF NOT EXISTS local_sucursales (
          id_sucursal INTEGER NOT NULL,
          id_empresa INTEGER NOT NULL,
          nombre TEXT NOT NULL,
          direccion TEXT,
          telefono TEXT,
          ciudad TEXT,
          raw_json TEXT NOT NULL,
          updated_at TEXT NOT NULL,
          PRIMARY KEY (id_sucursal, id_empresa)
        );
      ''');
      await db.execute('''
        CREATE TABLE IF NOT EXISTS local_pedidos (
          id_pedido INTEGER NOT NULL,
          id_empresa INTEGER NOT NULL,
          id_usuario INTEGER NOT NULL,
          codigo_pedido TEXT NOT NULL,
          estado TEXT NOT NULL,
          raw_json TEXT NOT NULL,
          created_at TEXT NOT NULL,
          PRIMARY KEY (id_pedido, id_empresa, id_usuario)
        );
      ''');
    }
    if (oldVersion < 3) {
      await db.execute('''
        CREATE TABLE IF NOT EXISTS local_devoluciones (
          id_devolucion INTEGER NOT NULL,
          id_empresa INTEGER NOT NULL,
          id_usuario INTEGER NOT NULL,
          id_venta INTEGER NOT NULL,
          codigo_venta TEXT,
          motivo TEXT NOT NULL,
          tipo_resolucion TEXT,
          estado TEXT NOT NULL,
          monto_reembolso REAL DEFAULT 0,
          items_json TEXT,
          created_at TEXT NOT NULL,
          PRIMARY KEY (id_devolucion, id_empresa)
        );
      ''');
      await _autoPoblarSucursalesIniciales(db);
      await _autoPoblarProductosIniciales(db);
    }
  }

  // ===========================================================================
  // MÉTODOS DE ACCESO MULTITENANT
  // ===========================================================================

  // --- TIENDAS / TENANTS ---
  Future<void> saveTenants(List<TenantModel> tenants) async {
    final db = await database;
    final batch = db.batch();
    final now = DateTime.now().toIso8601String();

    for (final t in tenants) {
      batch.insert(
        'local_tenants',
        {
          'id_empresa': t.idEmpresa,
          'nombre_empresa': t.nombreEmpresa,
          'slug': t.nombreEmpresa.toLowerCase().replaceAll(' ', '-'),
          'razon_social': t.razonSocial,
          'logo': t.logo,
          'ciudad': t.ciudad,
          'direccion_fiscal': t.direccionFiscal,
          'updated_at': now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit(noResult: true);
  }

  Future<List<TenantModel>> getTenants() async {
    final db = await database;
    final rows = await db.query('local_tenants', orderBy: 'id_empresa ASC');
    return rows.map((r) => TenantModel.fromJson(r)).toList();
  }

  // --- CATÁLOGO DE PRODUCTOS (PARTICIONADO POR TENANT) ---
  Future<void> saveProducts(int idEmpresa, List<PrendaModel> products) async {
    final db = await database;
    final batch = db.batch();
    final now = DateTime.now().toIso8601String();

    for (final p in products) {
      final rawMap = {
        'id_producto': p.idProducto,
        'id_empresa': idEmpresa,
        'id_categoria': p.idCategoria,
        'categoria_nombre': p.categoriaNombre,
        'codigo_producto': p.codigoProducto,
        'nombre': p.nombre,
        'descripcion': p.descripcion,
        'marca': p.marca,
        'genero': p.genero,
        'precio': p.precio,
        'promocion': p.promocion,
        'estado_stock': p.estadoStock,
        'stock_disponible_catalogo': p.stockDisponibleCatalogo,
        'imagen_principal': p.imagenPrincipal,
        'total_imagenes': p.totalImagenes,
        'total_variantes': p.totalVariantes,
        'tallas_disponibles': p.tallasDisponibles,
        'colores_disponibles': p.coloresDisponibles,
        'tiene_ra': p.tieneRa,
        'modelo_2d_url': p.modelo2dUrl,
        'tipo_prenda_ra': p.tipoPrendaRa,
      };

      batch.insert(
        'local_products',
        {
          'id_producto': p.idProducto,
          'id_empresa': idEmpresa,
          'id_categoria': p.idCategoria,
          'categoria_nombre': p.categoriaNombre,
          'codigo_producto': p.codigoProducto,
          'nombre': p.nombre,
          'descripcion': p.descripcion,
          'marca': p.marca,
          'genero': p.genero,
          'precio': p.precio,
          'estado_stock': p.estadoStock,
          'stock_disponible_catalogo': p.stockDisponibleCatalogo,
          'imagen_principal': p.imagenPrincipal,
          'tiene_ra': p.tieneRa ? 1 : 0,
          'raw_json': jsonEncode(rawMap),
          'updated_at': now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit(noResult: true);
  }

  Future<List<PrendaModel>> getProducts(
    int idEmpresa, {
    String? busqueda,
    int? categoriaId,
    double? precioMin,
    double? precioMax,
    String? orden,
  }) async {
    final db = await database;
    final whereClauses = <String>['id_empresa = ?'];
    final whereArgs = <dynamic>[idEmpresa];

    if (busqueda != null && busqueda.trim().isNotEmpty) {
      whereClauses.add('(nombre LIKE ? OR descripcion LIKE ? OR codigo_producto LIKE ?)');
      final term = '%${busqueda.trim()}%';
      whereArgs.addAll([term, term, term]);
    }

    if (categoriaId != null) {
      whereClauses.add('id_categoria = ?');
      whereArgs.add(categoriaId);
    }

    if (precioMin != null) {
      whereClauses.add('precio >= ?');
      whereArgs.add(precioMin);
    }

    if (precioMax != null) {
      whereClauses.add('precio <= ?');
      whereArgs.add(precioMax);
    }

    String orderBy = 'id_producto DESC';
    if (orden == 'precio_asc') {
      orderBy = 'precio ASC';
    } else if (orden == 'precio_desc') {
      orderBy = 'precio DESC';
    }

    var rows = await db.query(
      'local_products',
      where: whereClauses.join(' AND '),
      whereArgs: whereArgs,
      orderBy: orderBy,
      limit: 100,
    );

    // Auto-sembrar si la tabla está vacía y reintentar
    if (rows.isEmpty) {
      final totalInDb = Sqflite.firstIntValue(await db.rawQuery('SELECT COUNT(*) FROM local_products')) ?? 0;
      if (totalInDb == 0) {
        await _autoPoblarProductosIniciales(db);
        rows = await db.query(
          'local_products',
          where: whereClauses.join(' AND '),
          whereArgs: whereArgs,
          orderBy: orderBy,
          limit: 100,
        );
      }
    }

    // Fallback: si con filtro de empresa no hay nada pero hay prendas en SQLite, devolver las disponibles
    if (rows.isEmpty && idEmpresa > 0 && busqueda == null && categoriaId == null) {
      rows = await db.query('local_products', orderBy: orderBy, limit: 100);
    }

    return rows.map((r) {
      try {
        final map = jsonDecode(r['raw_json'] as String) as Map<String, dynamic>;
        return PrendaModel.fromJson(map);
      } catch (_) {
        return PrendaModel(
          idProducto: r['id_producto'] as int,
          idEmpresa: r['id_empresa'] as int,
          idCategoria: r['id_categoria'] as int? ?? 0,
          categoriaNombre: r['categoria_nombre'] as String? ?? '',
          codigoProducto: r['codigo_producto'] as String?,
          nombre: r['nombre'] as String? ?? '',
          descripcion: r['descripcion'] as String? ?? '',
          marca: r['marca'] as String? ?? '',
          genero: r['genero'] as String? ?? '',
          precio: (r['precio'] as num?)?.toDouble() ?? 0.0,
          imagenPrincipal: r['imagen_principal'] as String?,
          estadoStock: r['estado_stock'] as String? ?? 'DISPONIBLE',
          stockDisponibleCatalogo: r['stock_disponible_catalogo'] as int? ?? 0,
          tieneRa: (r['tiene_ra'] as int?) == 1,
        );
      }
    }).toList();
  }

  // --- DETALLES DE PRODUCTO (PARTICIONADO POR TENANT) ---
  Future<void> saveProductDetail(int idEmpresa, int idProducto, DetallePrendaModel detail) async {
    final db = await database;
    final now = DateTime.now().toIso8601String();

    final rawMap = {
      'id_producto': detail.idProducto,
      'id_empresa': idEmpresa,
      'empresa_nombre': detail.empresaNombre,
      'id_categoria': detail.idCategoria,
      'categoria_nombre': detail.categoriaNombre,
      'codigo_producto': detail.codigoProducto,
      'nombre': detail.nombre,
      'descripcion': detail.descripcion,
      'marca': detail.marca,
      'genero': detail.genero,
      'precio': detail.precio,
      'imagen_principal': detail.imagenPrincipal,
      'imagenes': detail.imagenes,
      'variantes': detail.variantes.map((v) => {
        'id_variante': v.idVariante,
        'id_talla': v.idTalla,
        'talla_nombre': v.tallaNombre,
        'id_color': v.idColor,
        'color_nombre': v.colorNombre,
        'codigo_hex': v.codigoHex,
        'sku': v.sku,
        'precio': v.precio,
      }).toList(),
      'tallas': detail.tallas,
      'colores': detail.colores,
      'stock_total_general': detail.stockTotalGeneral,
      'hay_stock_disponible': detail.hayStockDisponible,
      'permite_reserva': detail.permiteReserva,
      'permite_compra': detail.permiteCompra,
      'tiene_ra': detail.tieneRa,
      'modelo_2d_url': detail.modelo2dUrl,
      'tipo_prenda_ra': detail.tipoPrendaRa,
    };

    await db.insert(
      'local_product_details',
      {
        'id_producto': idProducto,
        'id_empresa': idEmpresa,
        'raw_json': jsonEncode(rawMap),
        'updated_at': now,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<DetallePrendaModel?> getProductDetail(int idEmpresa, int idProducto) async {
    final db = await database;
    List<Map<String, dynamic>> rows = [];
    if (idEmpresa > 0) {
      rows = await db.query(
        'local_product_details',
        where: 'id_empresa = ? AND id_producto = ?',
        whereArgs: [idEmpresa, idProducto],
        limit: 1,
      );
    }
    // Si no se encuentra con la empresa específica, buscar por id_producto global
    if (rows.isEmpty) {
      rows = await db.query(
        'local_product_details',
        where: 'id_producto = ?',
        whereArgs: [idProducto],
        limit: 1,
      );
    }

    if (rows.isEmpty) return null;
    try {
      final map = jsonDecode(rows.first['raw_json'] as String) as Map<String, dynamic>;
      return DetallePrendaModel.fromJson(map);
    } catch (_) {
      return null;
    }
  }

  /// Obtiene un producto básico de catálogo en SQLite para sintetizar vista offline
  Future<PrendaModel?> getProductById(int idEmpresa, int idProducto) async {
    final db = await database;
    List<Map<String, dynamic>> rows = [];
    if (idEmpresa > 0) {
      rows = await db.query(
        'local_products',
        where: 'id_empresa = ? AND id_producto = ?',
        whereArgs: [idEmpresa, idProducto],
        limit: 1,
      );
    }
    // Fallback a buscar por id_producto global
    if (rows.isEmpty) {
      rows = await db.query(
        'local_products',
        where: 'id_producto = ?',
        whereArgs: [idProducto],
        limit: 1,
      );
    }

    if (rows.isEmpty) {
      final totalInDb = Sqflite.firstIntValue(await db.rawQuery('SELECT COUNT(*) FROM local_products')) ?? 0;
      if (totalInDb == 0) {
        await _autoPoblarProductosIniciales(db);
        rows = await db.query(
          'local_products',
          where: 'id_producto = ?',
          whereArgs: [idProducto],
          limit: 1,
        );
      }
    }

    if (rows.isEmpty) return null;
    final r = rows.first;
    try {
      final map = jsonDecode(r['raw_json'] as String) as Map<String, dynamic>;
      return PrendaModel.fromJson(map);
    } catch (_) {
      return PrendaModel(
        idProducto: r['id_producto'] as int,
        idEmpresa: r['id_empresa'] as int,
        idCategoria: r['id_categoria'] as int? ?? 0,
        categoriaNombre: r['categoria_nombre'] as String? ?? '',
        codigoProducto: r['codigo_producto'] as String?,
        nombre: r['nombre'] as String? ?? '',
        descripcion: r['descripcion'] as String? ?? '',
        marca: r['marca'] as String? ?? '',
        genero: r['genero'] as String? ?? '',
        precio: (r['precio'] as num?)?.toDouble() ?? 0.0,
        imagenPrincipal: r['imagen_principal'] as String?,
        estadoStock: r['estado_stock'] as String? ?? 'DISPONIBLE',
        stockDisponibleCatalogo: r['stock_disponible_catalogo'] as int? ?? 0,
        tieneRa: (r['tiene_ra'] as int?) == 1,
      );
    }
  }

  /// Búsqueda inteligente de productos en catálogo local SQLite para el Asistente Offline
  Future<List<PrendaModel>> searchProductsOffline(String query, {int? idEmpresa}) async {
    final db = await database;
    final count = Sqflite.firstIntValue(await db.rawQuery('SELECT COUNT(*) FROM local_products')) ?? 0;
    if (count == 0) {
      await _autoPoblarProductosIniciales(db);
    }

    final cleanQuery = query.trim().toLowerCase();
    final whereClauses = <String>[];
    final whereArgs = <dynamic>[];

    if (idEmpresa != null && idEmpresa > 0) {
      whereClauses.add('id_empresa = ?');
      whereArgs.add(idEmpresa);
    }

    if (cleanQuery.isNotEmpty) {
      whereClauses.add('(LOWER(nombre) LIKE ? OR LOWER(descripcion) LIKE ? OR LOWER(marca) LIKE ? OR LOWER(categoria_nombre) LIKE ?)');
      final term = '%$cleanQuery%';
      whereArgs.addAll([term, term, term, term]);
    }

    var rows = await db.query(
      'local_products',
      where: whereClauses.isNotEmpty ? whereClauses.join(' AND ') : null,
      whereArgs: whereArgs.isNotEmpty ? whereArgs : null,
      orderBy: 'id_producto DESC',
      limit: 20,
    );

    // Si con filtro de empresa no hubo resultados pero sí hay búsqueda, relajar id_empresa
    if (rows.isEmpty && idEmpresa != null && cleanQuery.isNotEmpty) {
      rows = await db.query(
        'local_products',
        where: '(LOWER(nombre) LIKE ? OR LOWER(descripcion) LIKE ? OR LOWER(marca) LIKE ? OR LOWER(categoria_nombre) LIKE ?)',
        whereArgs: ['%$cleanQuery%', '%$cleanQuery%', '%$cleanQuery%', '%$cleanQuery%'],
        orderBy: 'id_producto DESC',
        limit: 20,
      );
    }

    // Si aún está vacío, devolver catálogo general
    if (rows.isEmpty) {
      rows = await db.query(
        'local_products',
        orderBy: 'id_producto DESC',
        limit: 10,
      );
    }

    return rows.map((r) {
      try {
        final map = jsonDecode(r['raw_json'] as String) as Map<String, dynamic>;
        return PrendaModel.fromJson(map);
      } catch (_) {
        return PrendaModel(
          idProducto: r['id_producto'] as int,
          idEmpresa: r['id_empresa'] as int,
          idCategoria: r['id_categoria'] as int? ?? 0,
          categoriaNombre: r['categoria_nombre'] as String? ?? '',
          codigoProducto: r['codigo_producto'] as String?,
          nombre: r['nombre'] as String? ?? '',
          descripcion: r['descripcion'] as String? ?? '',
          marca: r['marca'] as String? ?? '',
          genero: r['genero'] as String? ?? '',
          precio: (r['precio'] as num?)?.toDouble() ?? 0.0,
          imagenPrincipal: r['imagen_principal'] as String?,
          estadoStock: r['estado_stock'] as String? ?? 'DISPONIBLE',
          stockDisponibleCatalogo: r['stock_disponible_catalogo'] as int? ?? 0,
          tieneRa: (r['tiene_ra'] as int?) == 1,
        );
      }
    }).toList();
  }

  /// Conteo de productos locales para verificación de faltantes
  Future<int> countProducts(int idEmpresa) async {
    final db = await database;
    final res = await db.rawQuery(
      'SELECT COUNT(*) as cnt FROM local_products WHERE id_empresa = ?',
      [idEmpresa],
    );
    return Sqflite.firstIntValue(res) ?? 0;
  }

  Future<int> countSucursales(int idEmpresa) async {
    final db = await database;
    final res = await db.rawQuery(
      'SELECT COUNT(*) as cnt FROM local_sucursales WHERE id_empresa = ?',
      [idEmpresa],
    );
    return Sqflite.firstIntValue(res) ?? 0;
  }

  // --- FILTROS Y CATEGORÍAS EN CACHÉ LOCAL ---
  Future<void> saveFiltros(int idEmpresa, FiltrosCatalogoModel filtros) async {
    final db = await database;
    final now = DateTime.now().toIso8601String();
    await db.insert(
      'local_filtros',
      {
        'id_empresa': idEmpresa,
        'raw_json': jsonEncode(filtros.toJson()),
        'updated_at': now,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<FiltrosCatalogoModel?> getFiltros(int idEmpresa) async {
    final db = await database;
    final rows = await db.query(
      'local_filtros',
      where: 'id_empresa = ?',
      whereArgs: [idEmpresa],
      limit: 1,
    );
    if (rows.isEmpty) return null;
    try {
      final map = jsonDecode(rows.first['raw_json'] as String) as Map<String, dynamic>;
      return FiltrosCatalogoModel.fromJson(map);
    } catch (_) {
      return null;
    }
  }

  Future<List<CategoriaFiltroModel>> getCategoriasFromProducts(int idEmpresa) async {
    final db = await database;
    final rows = await db.rawQuery('''
      SELECT id_categoria, categoria_nombre, COUNT(*) as total
      FROM local_products
      WHERE id_empresa = ? AND id_categoria IS NOT NULL AND id_categoria > 0
      GROUP BY id_categoria, categoria_nombre
      ORDER BY total DESC
    ''', [idEmpresa]);

    return rows.map((r) => CategoriaFiltroModel(
      idCategoria: r['id_categoria'] as int,
      nombre: r['categoria_nombre'] as String? ?? 'General',
      totalPrendas: r['total'] as int? ?? 0,
    )).toList();
  }

  // --- BORRADOR DE CARRITO (AISLADO POR TENANT Y USUARIO) ---
  Future<void> saveCartDraft(int idEmpresa, int idUsuario, List<ItemCarritoModel> items) async {
    final db = await database;
    await db.transaction((txn) async {
      await txn.delete(
        'local_cart_drafts',
        where: 'id_empresa = ? AND id_usuario = ?',
        whereArgs: [idEmpresa, idUsuario],
      );

      final now = DateTime.now().toIso8601String();
      for (final it in items) {
        await txn.insert(
          'local_cart_drafts',
          {
            'id_empresa': idEmpresa,
            'id_usuario': idUsuario,
            'id_variante': it.idVariante,
            'id_producto': it.idProducto,
            'producto_nombre': it.productoNombre,
            'talla_nombre': it.tallaNombre,
            'color_nombre': it.colorNombre,
            'codigo_hex': it.codigoHex,
            'precio_unitario': it.precioUnitario,
            'cantidad': it.cantidad,
            'imagen_url': it.imagenUrl,
            'updated_at': now,
          },
          conflictAlgorithm: ConflictAlgorithm.replace,
        );
      }
    });
  }

  Future<List<ItemCarritoModel>> getCartDraft(int idEmpresa, int idUsuario) async {
    final db = await database;
    final rows = await db.query(
      'local_cart_drafts',
      where: 'id_empresa = ? AND id_usuario = ?',
      whereArgs: [idEmpresa, idUsuario],
      orderBy: 'id_variante ASC',
    );

    return rows.map((r) {
      final cant = r['cantidad'] as int? ?? 1;
      final prec = (r['precio_unitario'] as num?)?.toDouble() ?? 0.0;
      return ItemCarritoModel(
        idDetalleCarrito: 0,
        idVariante: r['id_variante'] as int,
        idProducto: r['id_producto'] as int,
        productoNombre: r['producto_nombre'] as String? ?? 'Prenda',
        tallaNombre: r['talla_nombre'] as String? ?? '',
        colorNombre: r['color_nombre'] as String? ?? '',
        codigoHex: r['codigo_hex'] as String? ?? '#000000',
        precioUnitario: prec,
        cantidad: cant,
        subtotal: cant * prec,
        stockDisponible: 99,
        disponible: true,
        imagenUrl: r['imagen_url'] as String?,
        advertenciaStock: 'Precio y stock sujetos a confirmación con la tienda.',
      );
    }).toList();
  }

  Future<void> clearCartDraft(int idEmpresa, int idUsuario) async {
    final db = await database;
    await db.delete(
      'local_cart_drafts',
      where: 'id_empresa = ? AND id_usuario = ?',
      whereArgs: [idEmpresa, idUsuario],
    );
  }

  // --- SUCURSALES (PARTICIONADO POR TENANT) ---
  Future<void> saveSucursales(int idEmpresa, List<SucursalContextModel> sucursales) async {
    final db = await database;
    final batch = db.batch();
    final now = DateTime.now().toIso8601String();

    for (final s in sucursales) {
      final rawMap = {
        'id_sucursal': s.idSucursal,
        'id_empresa': s.idEmpresa > 0 ? s.idEmpresa : idEmpresa,
        'nombre': s.nombre,
        'direccion': s.direccion,
        'telefono': s.telefono,
        'ciudad': s.ciudad,
      };

      batch.insert(
        'local_sucursales',
        {
          'id_sucursal': s.idSucursal,
          'id_empresa': s.idEmpresa > 0 ? s.idEmpresa : idEmpresa,
          'nombre': s.nombre,
          'direccion': s.direccion,
          'telefono': s.telefono,
          'ciudad': s.ciudad,
          'raw_json': jsonEncode(rawMap),
          'updated_at': now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit(noResult: true);
  }

  Future<List<SucursalContextModel>> getSucursales(int idEmpresa) async {
    final db = await database;
    List<Map<String, dynamic>> rows = [];

    if (idEmpresa > 0) {
      rows = await db.query(
        'local_sucursales',
        where: 'id_empresa = ?',
        whereArgs: [idEmpresa],
        orderBy: 'nombre ASC',
      );
    }

    // 1. Si no hay sucursales para este tenant o idEmpresa <= 0, buscar cualquier sucursal en SQLite
    if (rows.isEmpty) {
      rows = await db.query('local_sucursales', orderBy: 'nombre ASC');
    }

    // 2. Si la tabla está vacía, auto-sembrar sucursales canónicas
    if (rows.isEmpty) {
      await _autoPoblarSucursalesIniciales(db);
      if (idEmpresa > 0) {
        rows = await db.query(
          'local_sucursales',
          where: 'id_empresa = ?',
          whereArgs: [idEmpresa],
          orderBy: 'nombre ASC',
        );
      }
      if (rows.isEmpty) {
        rows = await db.query('local_sucursales', orderBy: 'nombre ASC');
      }
    }

    return rows.map((r) => SucursalContextModel(
      idSucursal: r['id_sucursal'] as int,
      idEmpresa: r['id_empresa'] as int,
      nombre: r['nombre'] as String? ?? 'Sucursal',
      direccion: r['direccion'] as String? ?? '',
      telefono: r['telefono'] as String?,
      ciudad: r['ciudad'] as String?,
    )).toList();
  }

  /// Auto-siembra de sucursales canónicas en SQLite para que el modo offline nunca quede desprovisto
  Future<void> _autoPoblarSucursalesIniciales(Database db) async {
    final now = DateTime.now().toIso8601String();
    final defaultBranches = [
      // Tenant 1: SHOPPING BOLIVIA
      {
        'id_sucursal': 1,
        'id_empresa': 1,
        'nombre': 'Sucursal Central Equipetrol',
        'direccion': 'Av. San Martín #450, Barrio Equipetrol',
        'telefono': '+591 3 3428900',
        'ciudad': 'Santa Cruz',
      },
      {
        'id_sucursal': 2,
        'id_empresa': 1,
        'nombre': 'Sucursal Calacoto',
        'direccion': 'Calle 21 de Calacoto #8200',
        'telefono': '+591 2 2794500',
        'ciudad': 'La Paz',
      },
      // Tenant 2: FASHIONWORLD BOLIVIA
      {
        'id_sucursal': 3,
        'id_empresa': 2,
        'nombre': 'Sucursal Central El Prado',
        'direccion': 'Av. 16 de Julio #1440, El Prado',
        'telefono': '+591 2 2315600',
        'ciudad': 'La Paz',
      },
      {
        'id_sucursal': 4,
        'id_empresa': 2,
        'nombre': 'Sucursal Cochabamba',
        'direccion': 'Av. Ballivián #620, El Prado',
        'telefono': '+591 4 4257800',
        'ciudad': 'Cochabamba',
      },
      // Tenant 3: URBAN STORE BOLIVIA
      {
        'id_sucursal': 5,
        'id_empresa': 3,
        'nombre': 'Urban Store Central',
        'direccion': 'Av. Montenegro #1120, San Miguel',
        'telefono': '+591 2 2773300',
        'ciudad': 'La Paz',
      },
      {
        'id_sucursal': 6,
        'id_empresa': 3,
        'nombre': 'Urban Store Santa Cruz',
        'direccion': 'Ventura Mall, 2do Nivel Local 45',
        'telefono': '+591 3 3889100',
        'ciudad': 'Santa Cruz',
      },
    ];

    final batch = db.batch();
    for (final b in defaultBranches) {
      batch.insert(
        'local_sucursales',
        {
          ...b,
          'raw_json': jsonEncode(b),
          'updated_at': now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit(noResult: true);
  }

  /// Auto-siembra de prendas canónicas para que el catálogo, detalle y asistente NUNCA mueran sin red
  Future<void> _autoPoblarProductosIniciales(Database db) async {
    final now = DateTime.now().toIso8601String();
    final defaultProducts = [
      // Tenant 1: SHOPPING BOLIVIA (id_empresa: 1)
      {
        'id_producto': 1,
        'id_empresa': 1,
        'id_categoria': 1,
        'categoria_nombre': 'Vestidos',
        'codigo_producto': 'VES-001',
        'nombre': 'Vestido Gala Imperial',
        'descripcion': 'Elegante vestido de gala confeccionado en satén premium con pedrería fina y caída estructurada.',
        'marca': 'Aurora Collection',
        'genero': 'FEMENINO',
        'precio': 680.0,
        'estado_stock': 'DISPONIBLE',
        'stock_disponible_catalogo': 18,
        'imagen_principal': 'https://images.unsplash.com/photo-1566174053879-31528523f8ae?w=800',
        'total_imagenes': 1,
        'total_variantes': 4,
        'tallas_disponibles': [
          {'id_talla': 1, 'nombre': 'S'},
          {'id_talla': 2, 'nombre': 'M'},
          {'id_talla': 3, 'nombre': 'L'},
        ],
        'colores_disponibles': [
          {'id_color': 1, 'nombre': 'Dorado', 'codigo_hex': '#D4AF37'},
          {'id_color': 2, 'nombre': 'Negro', 'codigo_hex': '#1A1A1A'},
        ],
        'tiene_ra': 1,
      },
      {
        'id_producto': 2,
        'id_empresa': 1,
        'id_categoria': 2,
        'categoria_nombre': 'Trajes',
        'codigo_producto': 'TRJ-002',
        'nombre': 'Traje Ejecutivo Sartorial',
        'descripcion': 'Corte italiano en pura lana virgen con forro jacquard y solapa clásica de dos botones.',
        'marca': 'Aurora Sartorial',
        'genero': 'MASCULINO',
        'precio': 850.0,
        'estado_stock': 'DISPONIBLE',
        'stock_disponible_catalogo': 12,
        'imagen_principal': 'https://images.unsplash.com/photo-1594938298603-c8148c4dae35?w=800',
        'total_imagenes': 1,
        'total_variantes': 4,
        'tallas_disponibles': [
          {'id_talla': 2, 'nombre': 'M'},
          {'id_talla': 3, 'nombre': 'L'},
          {'id_talla': 4, 'nombre': 'XL'},
        ],
        'colores_disponibles': [
          {'id_color': 3, 'nombre': 'Azul Marino', 'codigo_hex': '#0F2042'},
          {'id_color': 2, 'nombre': 'Negro', 'codigo_hex': '#1A1A1A'},
        ],
        'tiene_ra': 1,
      },
      {
        'id_producto': 3,
        'id_empresa': 1,
        'id_categoria': 3,
        'categoria_nombre': 'Blusas',
        'codigo_producto': 'BLU-003',
        'nombre': 'Blusa Seda Nocturna',
        'descripcion': 'Blusa en seda natural con botones de nácar y acabado satinado de lujo.',
        'marca': 'Aurora Collection',
        'genero': 'FEMENINO',
        'precio': 320.0,
        'estado_stock': 'DISPONIBLE',
        'stock_disponible_catalogo': 25,
        'imagen_principal': 'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa?w=800',
        'total_imagenes': 1,
        'total_variantes': 2,
        'tallas_disponibles': [
          {'id_talla': 1, 'nombre': 'S'},
          {'id_talla': 2, 'nombre': 'M'},
        ],
        'colores_disponibles': [
          {'id_color': 4, 'nombre': 'Champagne', 'codigo_hex': '#F7E7CE'},
          {'id_color': 5, 'nombre': 'Bordó', 'codigo_hex': '#800020'},
        ],
        'tiene_ra': 0,
      },

      // Tenant 2: FASHIONWORLD BOLIVIA (id_empresa: 2)
      {
        'id_producto': 101,
        'id_empresa': 2,
        'id_categoria': 1,
        'categoria_nombre': 'Vestidos',
        'codigo_producto': 'FW-VES-101',
        'nombre': 'Vestido Esmeralda Cocktail',
        'descripcion': 'Vestido midi drapeado en terciopelo esmeralda para veladas exclusivas.',
        'marca': 'FashionWorld Chic',
        'genero': 'FEMENINO',
        'precio': 590.0,
        'estado_stock': 'DISPONIBLE',
        'stock_disponible_catalogo': 14,
        'imagen_principal': 'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1?w=800',
        'total_imagenes': 1,
        'total_variantes': 2,
        'tallas_disponibles': [
          {'id_talla': 1, 'nombre': 'S'},
          {'id_talla': 2, 'nombre': 'M'},
        ],
        'colores_disponibles': [
          {'id_color': 6, 'nombre': 'Esmeralda', 'codigo_hex': '#50C878'},
        ],
        'tiene_ra': 1,
      },
      {
        'id_producto': 102,
        'id_empresa': 2,
        'id_categoria': 2,
        'categoria_nombre': 'Blazers',
        'codigo_producto': 'FW-BLZ-102',
        'nombre': 'Blazer Terciopelo Royal',
        'descripcion': 'Blazer de corte ajustado en terciopelo azul noche con botonadura metálica.',
        'marca': 'FashionWorld Bespoke',
        'genero': 'MASCULINO',
        'precio': 740.0,
        'estado_stock': 'DISPONIBLE',
        'stock_disponible_catalogo': 10,
        'imagen_principal': 'https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800',
        'total_imagenes': 1,
        'total_variantes': 2,
        'tallas_disponibles': [
          {'id_talla': 2, 'nombre': 'M'},
          {'id_talla': 3, 'nombre': 'L'},
        ],
        'colores_disponibles': [
          {'id_color': 3, 'nombre': 'Azul Marino', 'codigo_hex': '#0F2042'},
        ],
        'tiene_ra': 0,
      },

      // Tenant 3: URBAN STORE BOLIVIA (id_empresa: 3)
      {
        'id_producto': 201,
        'id_empresa': 3,
        'id_categoria': 4,
        'categoria_nombre': 'Chaquetas',
        'codigo_producto': 'URB-JKT-201',
        'nombre': 'Chaqueta Cuero Aviador Vintage',
        'descripcion': 'Cuero curtido vegetal de alta resistencia con detalles en borrego sintético.',
        'marca': 'Urban Street',
        'genero': 'UNISEX',
        'precio': 890.0,
        'estado_stock': 'DISPONIBLE',
        'stock_disponible_catalogo': 15,
        'imagen_principal': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=800',
        'total_imagenes': 1,
        'total_variantes': 4,
        'tallas_disponibles': [
          {'id_talla': 2, 'nombre': 'M'},
          {'id_talla': 3, 'nombre': 'L'},
          {'id_talla': 4, 'nombre': 'XL'},
        ],
        'colores_disponibles': [
          {'id_color': 7, 'nombre': 'Marrón Vintage', 'codigo_hex': '#4B2E1E'},
          {'id_color': 2, 'nombre': 'Negro', 'codigo_hex': '#1A1A1A'},
        ],
        'tiene_ra': 1,
      },
      {
        'id_producto': 202,
        'id_empresa': 3,
        'id_categoria': 1,
        'categoria_nombre': 'Vestidos',
        'codigo_producto': 'URB-VES-202',
        'nombre': 'Vestido Midi Urbano',
        'descripcion': 'Vestido de punto elástico contemporáneo, fresco y versátil para el día a día.',
        'marca': 'Urban Minimal',
        'genero': 'FEMENINO',
        'precio': 440.0,
        'estado_stock': 'DISPONIBLE',
        'stock_disponible_catalogo': 20,
        'imagen_principal': 'https://images.unsplash.com/photo-1496747611176-843222e1e57c?w=800',
        'total_imagenes': 1,
        'total_variantes': 2,
        'tallas_disponibles': [
          {'id_talla': 1, 'nombre': 'S'},
          {'id_talla': 2, 'nombre': 'M'},
        ],
        'colores_disponibles': [
          {'id_color': 8, 'nombre': 'Beige Arena', 'codigo_hex': '#C2B280'},
          {'id_color': 2, 'nombre': 'Negro', 'codigo_hex': '#1A1A1A'},
        ],
        'tiene_ra': 0,
      },
      {
        'id_producto': 203,
        'id_empresa': 3,
        'id_categoria': 6,
        'categoria_nombre': 'Sudaderas',
        'codigo_producto': 'URB-HD-203',
        'nombre': 'Hoodie Oversized Heavy Cotton',
        'descripcion': 'Sudadera pesada de 450 gsm en algodón orgánico peinado con acabados en canalé.',
        'marca': 'Urban Street',
        'genero': 'UNISEX',
        'precio': 380.0,
        'estado_stock': 'DISPONIBLE',
        'stock_disponible_catalogo': 30,
        'imagen_principal': 'https://images.unsplash.com/photo-1556905055-8f358a7a47b2?w=800',
        'total_imagenes': 1,
        'total_variantes': 3,
        'tallas_disponibles': [
          {'id_talla': 1, 'nombre': 'S'},
          {'id_talla': 2, 'nombre': 'M'},
          {'id_talla': 3, 'nombre': 'L'},
        ],
        'colores_disponibles': [
          {'id_color': 9, 'nombre': 'Gris Jaspe', 'codigo_hex': '#808080'},
          {'id_color': 2, 'nombre': 'Negro', 'codigo_hex': '#1A1A1A'},
        ],
        'tiene_ra': 0,
      },
    ];

    final batch = db.batch();
    for (final p in defaultProducts) {
      batch.insert(
        'local_products',
        {
          'id_producto': p['id_producto'],
          'id_empresa': p['id_empresa'],
          'id_categoria': p['id_categoria'],
          'categoria_nombre': p['categoria_nombre'],
          'codigo_producto': p['codigo_producto'],
          'nombre': p['nombre'],
          'descripcion': p['descripcion'],
          'marca': p['marca'],
          'genero': p['genero'],
          'precio': p['precio'],
          'estado_stock': p['estado_stock'],
          'stock_disponible_catalogo': p['stock_disponible_catalogo'],
          'imagen_principal': p['imagen_principal'],
          'tiene_ra': p['tiene_ra'],
          'raw_json': jsonEncode(p),
          'updated_at': now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit(noResult: true);
  }

  // --- PEDIDOS DEL USUARIO EN CACHÉ LOCAL ---
  Future<void> savePedidos(int idEmpresa, int idUsuario, List<PedidoModel> pedidos) async {
    final db = await database;
    final batch = db.batch();
    final now = DateTime.now().toIso8601String();

    for (final p in pedidos) {
      batch.insert(
        'local_pedidos',
        {
          'id_pedido': p.idPedido,
          'id_empresa': idEmpresa,
          'id_usuario': idUsuario,
          'codigo_pedido': p.codigoPedido,
          'estado': p.estado,
          'raw_json': jsonEncode(p.toJson()),
          'created_at': p.fechaPedido.isNotEmpty ? p.fechaPedido : now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit(noResult: true);
  }

  Future<List<PedidoModel>> getPedidos(int idEmpresa, int idUsuario) async {
    final db = await database;
    final rows = await db.query(
      'local_pedidos',
      where: 'id_empresa = ? AND id_usuario = ?',
      whereArgs: [idEmpresa, idUsuario],
      orderBy: 'created_at DESC',
    );

    return rows.map((r) {
      try {
        final map = jsonDecode(r['raw_json'] as String) as Map<String, dynamic>;
        return PedidoModel.fromJson(map);
      } catch (_) {
        return PedidoModel.fromJson(r);
      }
    }).toList();
  }

  // --- DEVOLUCIONES EN CACHÉ LOCAL ---
  Future<void> saveDevoluciones(int idEmpresa, int idUsuario, List<SolicitudDevolucionModel> devoluciones) async {
    final db = await database;
    final batch = db.batch();
    final now = DateTime.now().toIso8601String();

    for (final d in devoluciones) {
      batch.insert(
        'local_devoluciones',
        {
          'id_devolucion': d.idDevolucion,
          'id_empresa': idEmpresa,
          'id_usuario': idUsuario,
          'id_venta': d.idVenta,
          'codigo_venta': d.numeroVenta ?? 'VENTA-${d.idVenta}',
          'motivo': d.motivo,
          'tipo_resolucion': d.tipoResolucion,
          'estado': d.estado,
          'monto_reembolso': d.montoTotal,
          'items_json': jsonEncode(d.items.map((i) => i.toJson()).toList()),
          'created_at': d.fechaSolicitud.isNotEmpty ? d.fechaSolicitud : now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit(noResult: true);
  }

  Future<List<SolicitudDevolucionModel>> getDevoluciones(int idEmpresa, int idUsuario) async {
    final db = await database;
    final rows = await db.query(
      'local_devoluciones',
      where: 'id_empresa = ? AND id_usuario = ?',
      whereArgs: [idEmpresa, idUsuario],
      orderBy: 'created_at DESC',
    );

    return rows.map((r) {
      try {
        final map = jsonDecode(r['raw_json'] as String? ?? '{}') as Map<String, dynamic>;
        return SolicitudDevolucionModel.fromJson(map);
      } catch (_) {
        return SolicitudDevolucionModel.fromJson(r);
      }
    }).toList();
  }

  Future<void> saveDevolucionDraft(int idEmpresa, int idUsuario, SolicitudDevolucionModel solicitud) async {
    final db = await database;
    final now = DateTime.now().toIso8601String();
    final tempId = DateTime.now().millisecondsSinceEpoch ~/ 1000;

    await db.insert(
      'local_devoluciones',
      {
        'id_devolucion': tempId,
        'id_empresa': idEmpresa,
        'id_usuario': idUsuario,
        'id_venta': solicitud.idVenta,
        'codigo_venta': 'VENTA-${solicitud.idVenta}',
        'motivo': solicitud.motivo,
        'tipo_resolucion': solicitud.tipoResolucion,
        'estado': 'PENDIENTE_SYNC',
        'monto_reembolso': 0.0,
        'items_json': jsonEncode(solicitud.items.map((i) => i.toJson()).toList()),
        'created_at': now,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  // --- COLA DE SINCRONIZACIÓN (/api/sync/lote) ---
  Future<void> enqueueSyncOperation({
    required String operationId,
    required int idEmpresa,
    required int idUsuario,
    int? idSucursal,
    required String kind,
    required Map<String, dynamic> payload,
  }) async {
    final db = await database;
    final now = DateTime.now().toUtc().toIso8601String();

    await db.insert(
      'local_sync_operations',
      {
        'operation_id': operationId,
        'id_empresa': idEmpresa,
        'id_usuario': idUsuario,
        'id_sucursal': idSucursal,
        'kind': kind,
        'payload_json': jsonEncode(payload),
        'status': 'pending',
        'retry_count': 0,
        'created_at': now,
        'updated_at': now,
      },
      conflictAlgorithm: ConflictAlgorithm.ignore,
    );
  }

  Future<List<Map<String, dynamic>>> getPendingSyncOperations({int? idEmpresa, int? idUsuario}) async {
    final db = await database;
    final where = <String>["status IN ('pending', 'failed_retryable')"];
    final args = <dynamic>[];

    if (idEmpresa != null) {
      where.add('id_empresa = ?');
      args.add(idEmpresa);
    }
    if (idUsuario != null) {
      where.add('id_usuario = ?');
      args.add(idUsuario);
    }

    final rows = await db.query(
      'local_sync_operations',
      where: where.join(' AND '),
      whereArgs: args,
      orderBy: 'created_at ASC',
    );
    return rows;
  }

  Future<void> markSyncOperationResult({
    required String operationId,
    required String status,
    String? conflictCode,
    String? message,
    Map<String, dynamic>? responseData,
  }) async {
    final db = await database;
    final now = DateTime.now().toUtc().toIso8601String();

    await db.update(
      'local_sync_operations',
      {
        'status': status,
        'conflict_code': conflictCode,
        'message': message,
        'updated_at': now,
      },
      where: 'operation_id = ?',
      whereArgs: [operationId],
    );

    if (status == 'synced' && responseData != null) {
      await db.insert(
        'local_sync_receipts',
        {
          'operation_id': operationId,
          'id_empresa': responseData['id_empresa'] ?? 0,
          'id_usuario': responseData['id_usuario'] ?? 0,
          'response_json': jsonEncode(responseData),
          'created_at': now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
  }

  // --- RESERVAS LOCALES ---
  Future<void> saveLocalReservations(int idEmpresa, int idUsuario, List<ReservaModel> reservas) async {
    final db = await database;
    final batch = db.batch();
    final now = DateTime.now().toIso8601String();

    await db.delete(
      'local_reservations',
      where: 'id_empresa = ? AND id_usuario = ? AND is_offline_draft = 0',
      whereArgs: [idEmpresa, idUsuario],
    );

    for (final r in reservas) {
      batch.insert(
        'local_reservations',
        {
          'id_reserva_local': 'res_${r.idReserva}',
          'codigo_reserva': r.codigoReserva,
          'id_empresa': idEmpresa,
          'id_usuario': idUsuario,
          'id_sucursal': r.sucursal?.idSucursal,
          'sucursal_nombre': r.sucursal?.nombre,
          'fecha_hora_visita': r.fechaHoraVisita,
          'items_json': jsonEncode(r.items.map((i) => {
            'id_detalle_reserva': i.idDetalleReserva,
            'id_variante': i.idVariante,
            'cantidad': i.cantidad,
            'producto_nombre': i.productoNombre,
            'precio': i.precio,
            'talla': i.talla,
            'color': i.color,
            'codigo_hex': i.codigoHex,
            'imagen_url': i.imagenUrl,
          }).toList()),
          'observaciones': r.observaciones,
          'estado': r.estado,
          'is_offline_draft': 0,
          'created_at': now,
        },
        conflictAlgorithm: ConflictAlgorithm.replace,
      );
    }
    await batch.commit(noResult: true);
  }

  Future<void> saveReservationDraft({
    required String draftId,
    required int idEmpresa,
    required int idUsuario,
    required int idSucursal,
    required String sucursalNombre,
    required String fechaHoraVisita,
    required List<Map<String, dynamic>> items,
    String? observaciones,
  }) async {
    final db = await database;
    final now = DateTime.now().toIso8601String();

    await db.insert(
      'local_reservations',
      {
        'id_reserva_local': draftId,
        'codigo_reserva': 'BORRADOR-LOCAL',
        'id_empresa': idEmpresa,
        'id_usuario': idUsuario,
        'id_sucursal': idSucursal,
        'sucursal_nombre': sucursalNombre,
        'fecha_hora_visita': fechaHoraVisita,
        'items_json': jsonEncode(items),
        'observaciones': observaciones,
        'estado': 'PENDIENTE_SYNC',
        'is_offline_draft': 1,
        'created_at': now,
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<ReservaModel>> getLocalReservations(int idEmpresa, int idUsuario) async {
    final db = await database;
    final rows = await db.query(
      'local_reservations',
      where: 'id_empresa = ? AND id_usuario = ?',
      whereArgs: [idEmpresa, idUsuario],
      orderBy: 'created_at DESC',
    );

    return rows.map((r) {
      final itemsRaw = jsonDecode(r['items_json'] as String? ?? '[]') as List<dynamic>;
      final items = itemsRaw.map((e) => ItemReservaModel.fromJson(Map<String, dynamic>.from(e))).toList();
      final isDraft = (r['is_offline_draft'] as int? ?? 0) == 1;

      return ReservaModel(
        idReserva: int.tryParse(r['id_reserva_local'].toString().replaceAll('res_', '')) ?? 0,
        codigoReserva: r['codigo_reserva'] as String? ?? (isDraft ? 'BORRADOR' : ''),
        fechaReserva: r['created_at'] as String? ?? '',
        fechaHoraVisita: r['fecha_hora_visita'] as String? ?? '',
        estado: r['estado'] as String? ?? 'PENDIENTE',
        observaciones: r['observaciones'] as String?,
        sucursal: SucursalReservaModel(
          idSucursal: r['id_sucursal'] as int? ?? 0,
          nombre: r['sucursal_nombre'] as String? ?? 'Sucursal Tienda',
          direccion: '',
          ciudad: '',
        ),
        items: items,
        totalPrendas: items.length,
        conPago: false,
        estadoPago: 'GRATUITA',
        montoPagado: 0.0,
      );
    }).toList();
  }

  Future<List<ReservaModel>> getReservationDrafts(int idEmpresa, int idUsuario) => getLocalReservations(idEmpresa, idUsuario);

  // --- LIMPIEZA TOTAL EN LOGOUT ---
  Future<void> clearUserCache(int idUsuario) async {
    final db = await database;
    await db.delete('local_cart_drafts', where: 'id_usuario = ?', whereArgs: [idUsuario]);
    await db.delete('local_reservations', where: 'id_usuario = ?', whereArgs: [idUsuario]);
    await db.delete('local_devoluciones', where: 'id_usuario = ?', whereArgs: [idUsuario]);
  }
}
