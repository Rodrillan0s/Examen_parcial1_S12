import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:vector_math/vector_math_64.dart' hide Colors;
import 'package:aurora_store_mobile/features/virtual_try_on/domain/garment_transformer.dart';
import 'package:aurora_store_mobile/features/virtual_try_on/domain/smoothing_filter.dart';
import 'package:aurora_store_mobile/features/virtual_try_on/models/body_pose_model.dart';
import 'package:aurora_store_mobile/features/virtual_try_on/models/garment_model.dart';
import 'package:aurora_store_mobile/features/virtual_try_on/presentation/garment_size_selector.dart';

void main() {
  group('SmoothingFilter (EMA)', () {
    test('primer valor retornado directamente sin ponderación previa', () {
      final filter = SmoothingFilter(alpha: 0.35);
      final res = filter.smooth(
        x: 100.0,
        y: 200.0,
        scaleX: 50.0,
        scaleY: 60.0,
        rotation: 0.1,
      );

      expect(res.x, equals(100.0));
      expect(res.y, equals(200.0));
      expect(res.scaleX, equals(50.0));
      expect(res.scaleY, equals(60.0));
      expect(res.rotation, equals(0.1));
    });

    test('aplica ponderación exponencial correctamente en frames sucesivos', () {
      final filter = SmoothingFilter(alpha: 0.3); // 70% previo + 30% nuevo
      filter.smooth(
        x: 100.0,
        y: 100.0,
        scaleX: 100.0,
        scaleY: 100.0,
        rotation: 0.0,
      );

      final next = filter.smooth(
        x: 200.0,
        y: 200.0,
        scaleX: 200.0,
        scaleY: 200.0,
        rotation: 1.0,
      );

      // Esperado: 100 * 0.7 + 200 * 0.3 = 70 + 60 = 130
      expect(next.x, closeTo(130.0, 0.001));
      expect(next.y, closeTo(130.0, 0.001));
      expect(next.scaleX, closeTo(130.0, 0.001));
      expect(next.scaleY, closeTo(130.0, 0.001));
      expect(next.rotation, closeTo(0.3, 0.001));
    });

    test('reset() limpia la memoria temporal', () {
      final filter = SmoothingFilter(alpha: 0.3);
      filter.smooth(
        x: 100.0,
        y: 100.0,
        scaleX: 100.0,
        scaleY: 100.0,
        rotation: 0.0,
      );
      filter.reset();

      final res = filter.smooth(
        x: 500.0,
        y: 500.0,
        scaleX: 50.0,
        scaleY: 50.0,
        rotation: 0.5,
      );

      expect(res.x, equals(500.0));
      expect(res.y, equals(500.0));
    });
  });

  group('GarmentTransformer Geometry Engine', () {
    const screenSize = Size(400, 800);

    const topGarment = GarmentModel(
      idProducto: 4,
      nombre: 'Camiseta Silk Aurora',
      modelo2dUrl: 'https://res.cloudinary.com/demo/image/upload/camiseta.png',
      tipo: GarmentType.top,
      precio: 140.0,
    );

    const pantGarment = GarmentModel(
      idProducto: 6,
      nombre: 'Pantalón Lino Sartorial',
      modelo2dUrl: 'https://res.cloudinary.com/demo/image/upload/pantalon.png',
      tipo: GarmentType.pant,
      precio: 210.0,
    );

    const dressGarment = GarmentModel(
      idProducto: 5,
      nombre: 'Vestido Aurora Noir',
      modelo2dUrl: 'https://res.cloudinary.com/demo/image/upload/vestido.png',
      tipo: GarmentType.dress,
      precio: 320.0,
    );

    test('retorna hidden cuando el cuerpo no es detectado', () {
      final transformer = GarmentTransformer();
      const emptyPose = BodyPose();

      final transform = transformer.computeTransform(
        pose: emptyPose,
        garment: topGarment,
        screenSize: screenSize,
      );

      expect(transform.visible, isFalse);
    });

    test('calcula dimensiones y rotación correctas para prenda TOP', () {
      final transformer = GarmentTransformer();

      // Pose horizontal normalizada con hombros y cadera
      const pose = BodyPose(
        leftShoulder: BodyPoint(x: 0.4, y: 0.25, confidence: 0.9),
        rightShoulder: BodyPoint(x: 0.6, y: 0.25, confidence: 0.9),
        leftHip: BodyPoint(x: 0.42, y: 0.55, confidence: 0.9),
        rightHip: BodyPoint(x: 0.58, y: 0.55, confidence: 0.9),
      );

      final transform = transformer.computeTransform(
        pose: pose,
        garment: topGarment,
        screenSize: screenSize,
      );

      expect(transform.visible, isTrue);
      // Centro X de hombros: (0.4 + 0.6) / 2 = 0.5 * 400 = 200
      expect(transform.x, closeTo(200.0, 1.0));
      // Ancho debe ser mayor que el ancho de hombros
      expect(transform.width, greaterThan(100.0));
      expect(transform.height, greaterThan(100.0));
      // Hombros nivelados horizontalmente => rotación ~ 0
      expect(transform.rotation, closeTo(0.0, 0.05));
    });

    test('detecta inclinación y ángulo de rotación para TOP', () {
      final transformer = GarmentTransformer();

      // Hombro derecho inclinado hacia abajo (mayor Y)
      const pose = BodyPose(
        leftShoulder: BodyPoint(x: 0.4, y: 0.20, confidence: 0.9),
        rightShoulder: BodyPoint(x: 0.6, y: 0.30, confidence: 0.9),
      );

      final transform = transformer.computeTransform(
        pose: pose,
        garment: topGarment,
        screenSize: screenSize,
      );

      expect(transform.visible, isTrue);
      // El ángulo debe ser positivo por la inclinación hacia abajo en coordenadas de pantalla
      expect(transform.rotation, greaterThan(0.2));
    });

    test('calcula posición y dimensiones para prenda PANT', () {
      final transformer = GarmentTransformer();

      const pose = BodyPose(
        leftShoulder: BodyPoint(x: 0.4, y: 0.25, confidence: 0.9),
        rightShoulder: BodyPoint(x: 0.6, y: 0.25, confidence: 0.9),
        leftHip: BodyPoint(x: 0.43, y: 0.50, confidence: 0.9),
        rightHip: BodyPoint(x: 0.57, y: 0.50, confidence: 0.9),
        leftKnee: BodyPoint(x: 0.44, y: 0.75, confidence: 0.9),
        rightKnee: BodyPoint(x: 0.56, y: 0.75, confidence: 0.9),
      );

      final transform = transformer.computeTransform(
        pose: pose,
        garment: pantGarment,
        screenSize: screenSize,
      );

      expect(transform.visible, isTrue);
      // Centro X de cadera: (0.43 + 0.57) / 2 = 0.5 * 400 = 200
      expect(transform.x, closeTo(200.0, 1.0));
      // Y debe situarse debajo de la cadera (Y > 0.5 * 800 = 400)
      expect(transform.y, greaterThan(400.0));
    });

    test('calcula longitud proporcional para prenda DRESS', () {
      final transformer = GarmentTransformer();

      const pose = BodyPose(
        leftShoulder: BodyPoint(x: 0.4, y: 0.25, confidence: 0.9),
        rightShoulder: BodyPoint(x: 0.6, y: 0.25, confidence: 0.9),
        leftHip: BodyPoint(x: 0.42, y: 0.50, confidence: 0.9),
        rightHip: BodyPoint(x: 0.58, y: 0.50, confidence: 0.9),
        leftKnee: BodyPoint(x: 0.43, y: 0.75, confidence: 0.9),
        rightKnee: BodyPoint(x: 0.57, y: 0.75, confidence: 0.9),
      );

      final dressTransform = transformer.computeTransform(
        pose: pose,
        garment: dressGarment,
        screenSize: screenSize,
      );

      final topTransform = transformer.computeTransform(
        pose: pose,
        garment: topGarment,
        screenSize: screenSize,
      );

      expect(dressTransform.visible, isTrue);
      // El vestido debe ser más largo que el top
      expect(dressTransform.height, greaterThan(topTransform.height));
    });

    test('conserva última pose válida hasta 5 frames en pérdida momentánea', () {
      final transformer = GarmentTransformer();

      const validPose = BodyPose(
        leftShoulder: BodyPoint(x: 0.4, y: 0.25, confidence: 0.9),
        rightShoulder: BodyPoint(x: 0.6, y: 0.25, confidence: 0.9),
      );
      const emptyPose = BodyPose();

      final first = transformer.computeTransform(
        pose: validPose,
        garment: topGarment,
        screenSize: screenSize,
      );
      expect(first.visible, isTrue);

      // Frames 1 a 5 sin pose: debe mantenerse visible para evitar parpadeo
      for (int i = 1; i <= 5; i++) {
        final held = transformer.computeTransform(
          pose: emptyPose,
          garment: topGarment,
          screenSize: screenSize,
        );
        expect(held.visible, isTrue, reason: 'Frame $i debería conservar la pose');
      }

      // Frame 6 sin pose: debe ocultarse
      final hidden = transformer.computeTransform(
        pose: emptyPose,
        garment: topGarment,
        screenSize: screenSize,
      );
      expect(hidden.visible, isFalse, reason: 'Frame 6 debería ocultar la prenda');
    });

    test('escala dinámicamente las dimensiones según la talla (XS < S < M < L < XL)', () {
      final transformer = GarmentTransformer();

      const pose = BodyPose(
        leftShoulder: BodyPoint(x: 0.35, y: 0.25, confidence: 0.95),
        rightShoulder: BodyPoint(x: 0.65, y: 0.25, confidence: 0.95),
        leftHip: BodyPoint(x: 0.38, y: 0.55, confidence: 0.9),
        rightHip: BodyPoint(x: 0.62, y: 0.55, confidence: 0.9),
      );

      // Talla S (0.94x)
      final transS = transformer.computeTransform(
        pose: pose,
        garment: topGarment,
        screenSize: screenSize,
        sizeScale: 0.94,
      );

      transformer.reset();
      // Talla M (1.00x)
      final transM = transformer.computeTransform(
        pose: pose,
        garment: topGarment,
        screenSize: screenSize,
        sizeScale: 1.00,
      );

      transformer.reset();
      // Talla XL (1.25x)
      final transXL = transformer.computeTransform(
        pose: pose,
        garment: topGarment,
        screenSize: screenSize,
        sizeScale: 1.25,
      );

      expect(transS.visible, isTrue);
      expect(transM.visible, isTrue);
      expect(transXL.visible, isTrue);

      // La talla XL debe ser más ancha y larga que la M, y la M mayor que la S
      expect(transXL.width, greaterThan(transM.width));
      expect(transM.width, greaterThan(transS.width));
      expect(transXL.height, greaterThan(transM.height));
      expect(transM.height, greaterThan(transS.height));
    });

    test('el cuello de la prenda se alinea con las clavículas y hombros, no con el abdomen', () {
      final transformer = GarmentTransformer();

      const pose = BodyPose(
        leftShoulder: BodyPoint(x: 0.4, y: 0.20, confidence: 0.9),
        rightShoulder: BodyPoint(x: 0.6, y: 0.20, confidence: 0.9),
        leftHip: BodyPoint(x: 0.42, y: 0.55, confidence: 0.9),
        rightHip: BodyPoint(x: 0.58, y: 0.55, confidence: 0.9),
      );

      final transform = transformer.computeTransform(
        pose: pose,
        garment: topGarment,
        screenSize: screenSize,
      );

      expect(transform.visible, isTrue);

      // El hombro está en y = 0.20 * 800 = 160px
      const shoulderY = 0.20 * 800;
      final topCollarY = transform.y - (transform.height / 2.0);

      // El cuello debe iniciar levemente por encima del centro de hombros (~ clavícula)
      // y nunca por debajo de la altura de los hombros hacia el abdomen
      expect(topCollarY, lessThanOrEqualTo(shoulderY + 10.0));
      expect(topCollarY, greaterThan(shoulderY - 80.0));
    });

    test('BodyPose detecta correctamente la presencia de brazos y codos', () {
      const poseSinBrazos = BodyPose(
        leftShoulder: BodyPoint(x: 0.4, y: 0.25, confidence: 0.9),
        rightShoulder: BodyPoint(x: 0.6, y: 0.25, confidence: 0.9),
      );
      expect(poseSinBrazos.hasArms, isFalse);

      const poseConBrazos = BodyPose(
        leftShoulder: BodyPoint(x: 0.35, y: 0.25, confidence: 0.9),
        rightShoulder: BodyPoint(x: 0.65, y: 0.25, confidence: 0.9),
        leftElbow: BodyPoint(x: 0.25, y: 0.45, confidence: 0.85),
        rightElbow: BodyPoint(x: 0.75, y: 0.45, confidence: 0.85),
        leftWrist: BodyPoint(x: 0.20, y: 0.60, confidence: 0.80),
        rightWrist: BodyPoint(x: 0.80, y: 0.60, confidence: 0.80),
      );
      expect(poseConBrazos.hasArms, isTrue);
      expect(poseConBrazos.hasFullArms, isTrue);
      expect(poseConBrazos.hasForearms, isTrue);
    });

    test('isQuadConvex valida correctamente cuadriláteros convexos y descarta degenerados', () {
      // Trapecio anatómico convexo
      final quadConvexo = [
        const Offset(100, 100),
        const Offset(300, 100),
        const Offset(270, 350),
        const Offset(130, 350),
      ];
      expect(GarmentTransformer.isQuadConvex(quadConvexo), isTrue);

      // Cuadrilátero en forma de reloj de arena (auto-intersecante)
      final quadCruzado = [
        const Offset(100, 100),
        const Offset(300, 350),
        const Offset(300, 100),
        const Offset(100, 350),
      ];
      expect(GarmentTransformer.isQuadConvex(quadCruzado), isFalse);
    });

    test('computePerspectiveMatrix mapea esquinas de origen a los 4 puntos destino', () {
      final quad = [
        const Offset(50, 60),   // P0: Top-Left
        const Offset(250, 70),  // P1: Top-Right
        const Offset(230, 380), // P2: Bottom-Right
        const Offset(70, 370),  // P3: Bottom-Left
      ];

      const sourceWidth = 300.0;
      const sourceHeight = 400.0;

      final matrix = GarmentTransformer.computePerspectiveMatrix(
        sourceWidth,
        sourceHeight,
        quad,
      );

      expect(matrix, isNotNull);

      // Verificar que (0, 0) mapee a P0
      final v0 = matrix!.perspectiveTransform(Vector3(0, 0, 0));
      expect(v0.x, closeTo(50.0, 0.5));
      expect(v0.y, closeTo(60.0, 0.5));

      // Verificar que (sourceWidth, 0) mapee a P1
      final v1 = matrix.perspectiveTransform(Vector3(sourceWidth, 0, 0));
      expect(v1.x, closeTo(250.0, 0.5));
      expect(v1.y, closeTo(70.0, 0.5));

      // Verificar que (sourceWidth, sourceHeight) mapee a P2
      final v2 = matrix.perspectiveTransform(Vector3(sourceWidth, sourceHeight, 0));
      expect(v2.x, closeTo(230.0, 0.5));
      expect(v2.y, closeTo(380.0, 0.5));

      // Verificar que (0, sourceHeight) mapee a P3
      final v3 = matrix.perspectiveTransform(Vector3(0, sourceHeight, 0));
      expect(v3.x, closeTo(70.0, 0.5));
      expect(v3.y, closeTo(370.0, 0.5));
    });

    test('Warping de 4 puntos activo para prenda TOP cuando hombros y cadera están presentes', () {
      final transformer = GarmentTransformer();

      const pose = BodyPose(
        leftShoulder: BodyPoint(x: 0.35, y: 0.25, confidence: 0.95),
        rightShoulder: BodyPoint(x: 0.65, y: 0.25, confidence: 0.95),
        leftHip: BodyPoint(x: 0.38, y: 0.55, confidence: 0.9),
        rightHip: BodyPoint(x: 0.62, y: 0.55, confidence: 0.9),
      );

      final transform = transformer.computeTransform(
        pose: pose,
        garment: topGarment,
        screenSize: screenSize,
      );

      expect(transform.visible, isTrue);
      expect(transform.usePerspective, isTrue);
      expect(transform.perspectiveTransform, isNotNull);
      expect(transform.quadPoints, isNotNull);
      expect(transform.quadPoints!.length, equals(4));

      // P0 (top-left) debe estar a la izquierda de P1 (top-right)
      expect(transform.quadPoints![0].dx, lessThan(transform.quadPoints![1].dx));
      // P3 (bottom-left) debe estar a la izquierda de P2 (bottom-right)
      expect(transform.quadPoints![3].dx, lessThan(transform.quadPoints![2].dx));
      // Hombros deben estar arriba de las caderas
      expect(transform.quadPoints![0].dy, lessThan(transform.quadPoints![3].dy));
      expect(transform.quadPoints![1].dy, lessThan(transform.quadPoints![2].dy));
    });

    test('seguimiento dinámico de brazos eleva la manga P0 al levantar el brazo', () {
      final transformer = GarmentTransformer();

      // Pose con brazo izquierdo relajado hacia abajo
      const relaxedPose = BodyPose(
        leftShoulder: BodyPoint(x: 0.35, y: 0.25, confidence: 0.95),
        rightShoulder: BodyPoint(x: 0.65, y: 0.25, confidence: 0.95),
        leftElbow: BodyPoint(x: 0.30, y: 0.45, confidence: 0.90), // Codo abajo
        rightElbow: BodyPoint(x: 0.70, y: 0.45, confidence: 0.90),
        leftHip: BodyPoint(x: 0.38, y: 0.55, confidence: 0.9),
        rightHip: BodyPoint(x: 0.62, y: 0.55, confidence: 0.9),
      );

      final relaxedTransform = transformer.computeTransform(
        pose: relaxedPose,
        garment: topGarment,
        screenSize: screenSize,
      );

      transformer.reset();

      // Pose con brazo izquierdo levantado hacia arriba
      const raisedPose = BodyPose(
        leftShoulder: BodyPoint(x: 0.35, y: 0.25, confidence: 0.95),
        rightShoulder: BodyPoint(x: 0.65, y: 0.25, confidence: 0.95),
        leftElbow: BodyPoint(x: 0.25, y: 0.12, confidence: 0.90), // Codo ARRIBA (menor Y)
        rightElbow: BodyPoint(x: 0.70, y: 0.45, confidence: 0.90),
        leftHip: BodyPoint(x: 0.38, y: 0.55, confidence: 0.9),
        rightHip: BodyPoint(x: 0.62, y: 0.55, confidence: 0.9),
      );

      final raisedTransform = transformer.computeTransform(
        pose: raisedPose,
        garment: topGarment,
        screenSize: screenSize,
      );

      expect(relaxedTransform.quadPoints, isNotNull);
      expect(raisedTransform.quadPoints, isNotNull);

      // Al levantar el brazo, P0 (manga izquierda) debe elevarse (su coordenada Y debe disminuir)
      expect(raisedTransform.quadPoints![0].dy, lessThan(relaxedTransform.quadPoints![0].dy));
    });

    test('seguimiento dinámico de piernas adapta bajos del pantalón al separar las piernas', () {
      final transformer = GarmentTransformer();

      // Pose con piernas juntas
      const narrowPose = BodyPose(
        leftHip: BodyPoint(x: 0.45, y: 0.50, confidence: 0.95),
        rightHip: BodyPoint(x: 0.55, y: 0.50, confidence: 0.95),
        leftKnee: BodyPoint(x: 0.46, y: 0.70, confidence: 0.90),
        rightKnee: BodyPoint(x: 0.54, y: 0.70, confidence: 0.90),
        leftAnkle: BodyPoint(x: 0.46, y: 0.90, confidence: 0.90),
        rightAnkle: BodyPoint(x: 0.54, y: 0.90, confidence: 0.90),
      );

      final narrowTransform = transformer.computeTransform(
        pose: narrowPose,
        garment: pantGarment,
        screenSize: screenSize,
      );

      transformer.reset();

      // Pose con piernas abiertas / separadas
      const widePose = BodyPose(
        leftHip: BodyPoint(x: 0.45, y: 0.50, confidence: 0.95),
        rightHip: BodyPoint(x: 0.55, y: 0.50, confidence: 0.95),
        leftKnee: BodyPoint(x: 0.30, y: 0.70, confidence: 0.90),
        rightKnee: BodyPoint(x: 0.70, y: 0.70, confidence: 0.90),
        leftAnkle: BodyPoint(x: 0.20, y: 0.90, confidence: 0.90), // Tobillo izquierdo abierto
        rightAnkle: BodyPoint(x: 0.80, y: 0.90, confidence: 0.90), // Tobillo derecho abierto
      );

      final wideTransform = transformer.computeTransform(
        pose: widePose,
        garment: pantGarment,
        screenSize: screenSize,
      );

      expect(narrowTransform.quadPoints, isNotNull);
      expect(wideTransform.quadPoints, isNotNull);

      // Separación de bajos en pose estrecha: P1.dx - P0.dx
      final narrowSpan = narrowTransform.quadPoints![1].dx - narrowTransform.quadPoints![0].dx;
      // Separación de bajos en pose abierta: P2.dx - P3.dx
      final wideSpan = wideTransform.quadPoints![2].dx - wideTransform.quadPoints![3].dx;

      expect(wideSpan, greaterThan(narrowSpan));
      expect(wideTransform.width, greaterThan(narrowTransform.width));
    });

    test('GarmentModel parsea tallasDisponibles desde JSON correctamente', () {
      final json = {
        'id_producto': 4,
        'nombre': 'Vestido Sirena',
        'modelo_2d_url': 'https://res.cloudinary.com/demo/vestido.png',
        'tipo_prenda_ra': 'TOP',
        'precio': 1850.0,
        'tallas_disponibles': ['S', 'M', 'L'],
      };

      final garment = GarmentModel.fromJson(json);

      expect(garment.tallasDisponibles, equals(['S', 'M', 'L']));
      expect(garment.tallasDisponibles.contains('XL'), isFalse);
      expect(garment.tallasDisponibles.contains('XXL'), isFalse);
    });

    testWidgets('GarmentSizeSelector renderiza únicamente tallas disponibles de la prenda', (tester) async {
      String selected = 'S';

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: GarmentSizeSelector(
              selectedSize: selected,
              sizes: const ['S', 'M', 'L'],
              onSizeSelected: (s) => selected = s,
            ),
          ),
        ),
      );

      // Debe mostrar S, M, L
      expect(find.text('S'), findsOneWidget);
      expect(find.text('M'), findsOneWidget);
      expect(find.text('L'), findsOneWidget);

      // NO debe mostrar XS, XL, XXL porque no están disponibles en la prenda
      expect(find.text('XS'), findsNothing);
      expect(find.text('XL'), findsNothing);
      expect(find.text('XXL'), findsNothing);
    });
  });
}
