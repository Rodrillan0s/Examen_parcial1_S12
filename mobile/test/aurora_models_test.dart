import 'package:flutter_test/flutter_test.dart';
import 'package:aurora_store_mobile/services/auth_service.dart';
import 'package:aurora_store_mobile/services/catalogo_service.dart';
import 'package:aurora_store_mobile/services/carrito_service.dart';
import 'package:aurora_store_mobile/services/pedido_service.dart';
import 'package:aurora_store_mobile/services/pago_service.dart';
import 'package:aurora_store_mobile/services/reserva_service.dart';
import 'package:aurora_store_mobile/services/asistente_service.dart';

void main() {
  group('Aurora Store Mobile Model Tests', () {
    test('UsuarioModel parsing test (M01, M02)', () {
      final json = {
        'nro_usuario': 10,
        'correo': 'cliente@aurora.com',
        'nombre_usuario': 'cliente_aurora',
        'nombre': 'Valeria',
        'apellido': 'Mendoza',
        'id_rol': 2,
        'nombre_rol': 'Cliente',
        'id_empresa': 1,
        'nombre_empresa': 'SHOPPING BOLIVIA',
      };

      final u = UsuarioModel.fromJson(json);
      expect(u.nroUsuario, 10);
      expect(u.correo, 'cliente@aurora.com');
      expect(u.nombreCompleto, 'Valeria Mendoza');
      expect(u.idEmpresa, 1);
    });

    test('PrendaModel & DetallePrendaModel parsing test (M04, M06, M07)', () {
      final prendaJson = {
        'id_producto': 9,
        'id_empresa': 1,
        'id_categoria': 5,
        'categoria_nombre': 'Alta Costura & Gala',
        'nombre': 'Vestido de gala Aurora',
        'descripcion': 'Vestido exclusivo en seda',
        'marca': 'Aurora Atelier',
        'genero': 'Femenino',
        'precio': 800.0,
        'tallas_disponibles': [{'id_talla': 3, 'nombre': 'M'}],
        'colores_disponibles': [{'id_color': 10, 'nombre': 'Azul Noche', 'codigo_hex': '#191970'}],
      };

      final p = PrendaModel.fromJson(prendaJson);
      expect(p.idProducto, 9);
      expect(p.nombre, 'Vestido de gala Aurora');
      expect(p.precio, 800.0);
      expect(p.coloresDisponibles.length, 1);

      final detalleJson = {
        'id_producto': 9,
        'id_empresa': 1,
        'empresa_nombre': 'SHOPPING BOLIVIA',
        'id_categoria': 5,
        'categoria_nombre': 'Alta Costura & Gala',
        'nombre': 'Vestido de gala Aurora',
        'descripcion': 'Vestido exclusivo en seda',
        'marca': 'Aurora Atelier',
        'genero': 'Femenino',
        'precio': 800.0,
        'imagenes': ['https://example.com/img1.jpg'],
        'variantes': [
          {
            'id_variante': 15,
            'id_talla': 3,
            'talla_nombre': 'M',
            'id_color': 10,
            'color_nombre': 'Azul Noche',
            'codigo_hex': '#191970',
            'precio': 800.0,
          }
        ],
        'tallas': [{'id_talla': 3, 'nombre': 'M'}],
        'colores': [{'id_color': 10, 'nombre': 'Azul Noche', 'codigo_hex': '#191970'}],
        'stock_total_general': 12,
        'hay_stock_disponible': true,
        'permite_reserva': true,
        'permite_compra': true,
      };

      final dp = DetallePrendaModel.fromJson(detalleJson);
      expect(dp.variantes.length, 1);
      expect(dp.variantes.first.colorNombre, 'Azul Noche');
      expect(dp.stockTotalGeneral, 12);
      expect(dp.hayStockDisponible, true);
    });

    test('CarritoModel parsing test (M08)', () {
      final carritoJson = {
        'id_carrito': 101,
        'id_empresa': 1,
        'nombre_empresa': 'SHOPPING BOLIVIA',
        'items': [
          {
            'id_detalle_carrito': 1,
            'id_variante': 15,
            'id_producto': 9,
            'producto_nombre': 'Vestido de gala Aurora',
            'talla_nombre': 'M',
            'color_nombre': 'Azul Noche',
            'codigo_hex': '#191970',
            'cantidad': 2,
            'precio_unitario': 800.0,
            'subtotal': 1600.0,
            'stock_disponible': 5,
            'disponible': true,
          }
        ],
        'total_items': 2,
        'subtotal': 1600.0,
        'descuento': 0.0,
        'total': 1600.0,
        'puede_continuar_compra': true,
      };

      final c = CarritoModel.fromJson(carritoJson);
      expect(c.totalItems, 2);
      expect(c.total, 1600.0);
      expect(c.items.first.cantidad, 2);
    });

    test('PedidoModel parsing test (M09, M11)', () {
      final pedidoJson = {
        'id_pedido': 50,
        'codigo_pedido': 'PED-2026-00050',
        'fecha_pedido': '2026-09-19 12:00',
        'estado': 'PENDIENTE',
        'estado_pago': 'PAGADO',
        'modalidad_compra': 'RETIRO_SUCURSAL',
        'nombre_contacto': 'Valeria Mendoza',
        'telefono_contacto': '+591 70011223',
        'sucursal_nombre': 'Sucursal Central Equipetrol',
        'subtotal': 800.0,
        'costo_envio': 0.0,
        'descuento': 0.0,
        'total': 800.0,
        'total_items': 1,
        'items': [
          {
            'id_detalle_pedido': 1,
            'id_variante': 15,
            'producto_nombre': 'Vestido de gala Aurora',
            'talla_nombre': 'M',
            'color_nombre': 'Azul Noche',
            'codigo_hex': '#191970',
            'cantidad': 1,
            'precio_unitario': 800.0,
            'subtotal': 800.0,
          }
        ],
      };

      final ped = PedidoModel.fromJson(pedidoJson);
      expect(ped.codigoPedido, 'PED-2026-00050');
      expect(ped.estadoPago, 'PAGADO');
      expect(ped.items.length, 1);
    });

    test('ReservaModel parsing test (M10)', () {
      final reservaJson = {
        'id_reserva': 20,
        'codigo_reserva': 'RES-2026-00020',
        'fecha_reserva': '2026-09-19',
        'fecha_hora_visita': '2026-09-20 16:30',
        'estado': 'PENDIENTE',
        'total_prendas': 1,
        'sucursal': {
          'id_sucursal': 1,
          'nombre': 'Sucursal Central Equipetrol',
          'direccion': 'Av. San Martín #800',
          'ciudad': 'Santa Cruz',
        },
        'items': [
          {
            'id_detalle_reserva': 1,
            'id_variante': 15,
            'cantidad': 1,
            'producto_nombre': 'Vestido de gala Aurora',
            'precio': 800.0,
            'talla': 'M',
            'color': 'Azul Noche',
            'codigo_hex': '#191970',
          }
        ],
      };

      final r = ReservaModel.fromJson(reservaJson);
      expect(r.codigoReserva, 'RES-2026-00020');
      expect(r.sucursal?.nombre, 'Sucursal Central Equipetrol');
      expect(r.items.first.talla, 'M');
    });

    test('ChatMessageModel test (M13)', () {
      final msg = ChatMessageModel(
        id: 'msg_1',
        role: 'assistant',
        content: 'Tenemos vestidos de gala disponibles en color Azul Noche.',
        timestamp: DateTime.now(),
        tipo: 'texto',
      );
      expect(msg.role, 'assistant');
      expect(msg.content.contains('Azul Noche'), true);
    });

    test('ResumenPedidoPagoModel & ResultadoPagoModel parsing test (M09 Pago)', () {
      final resumenJson = {
        'id_pedido': 50,
        'codigo_pedido': 'PED-2026-00050',
        'id_cliente': 10,
        'id_empresa': 1,
        'id_sucursal': 1,
        'estado': 'PENDIENTE',
        'estado_pago': 'PENDIENTE_PAGO',
        'subtotal': 1200.0,
        'costo_envio': 0.0,
        'descuento': 0.0,
        'total': 1200.0,
        'correo_contacto': 'cliente@aurora.com',
        'nombre_contacto': 'Valeria Mendoza',
        'sucursal_nombre': 'Sucursal Equipetrol',
        'nombre_empresa': 'AURA Atelier',
        'items': [
          {
            'id_variante': 15,
            'cantidad': 1,
            'precio_unitario': 1200.0,
            'subtotal': 1200.0,
            'producto_nombre': 'Vestido de Seda Exclusivo',
            'talla': 'M',
            'color': 'Dorado',
          }
        ],
      };

      final resumen = ResumenPedidoPagoModel.fromJson(resumenJson);
      expect(resumen.idPedido, 50);
      expect(resumen.codigoPedido, 'PED-2026-00050');
      expect(resumen.total, 1200.0);
      expect(resumen.items.length, 1);
      expect(resumen.items.first.productoNombre, 'Vestido de Seda Exclusivo');

      final resultadoJson = {
        'id_pedido': 50,
        'codigo_pedido': 'PED-2026-00050',
        'id_venta': 12,
        'numero_venta': 'VTA-00012',
        'tipo_documento': 'FACTURA',
        'total': 1200.0,
        'metodo_pago': 'TARJETA',
        'codigo_transaccion': 'AUTH-9F3A12-4242',
        'url_descarga_pdf': '/api/comprobantes/venta/12/pdf',
      };

      final resultado = ResultadoPagoModel.fromJson(resultadoJson);
      expect(resultado.idVenta, 12);
      expect(resultado.numeroVenta, 'VTA-00012');
      expect(resultado.tipoDocumento, 'FACTURA');
      expect(resultado.metodoPago, 'TARJETA');
    });
  });
}
