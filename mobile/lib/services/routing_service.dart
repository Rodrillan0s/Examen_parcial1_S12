import 'package:dio/dio.dart';
import 'package:latlong2/latlong.dart';

class RoutingService {
  final Dio _dio = Dio(
    BaseOptions(
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
    ),
  );

  Future<List<LatLng>> obtenerRutaPorCalles({
    required LatLng origen,
    required LatLng destino,
  }) async {
    try {
      final url =
          'https://router.project-osrm.org/route/v1/driving/'
          '${origen.longitude},${origen.latitude};'
          '${destino.longitude},${destino.latitude}'
          '?overview=full&geometries=geojson';

      final response = await _dio.get(url);
      final data = response.data;

      final routes = data['routes'] as List?;
      if (routes == null || routes.isEmpty) {
        return [origen, destino];
      }

      final coordinates =
          routes.first['geometry']['coordinates'] as List<dynamic>;

      return coordinates.map((coord) {
        final lng = coord[0] as num;
        final lat = coord[1] as num;

        return LatLng(
          lat.toDouble(),
          lng.toDouble(),
        );
      }).toList();
    } catch (_) {
      return [origen, destino];
    }
  }
}