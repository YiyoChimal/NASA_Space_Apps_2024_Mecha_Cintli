import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:provider/provider.dart';
import '../../../core/provider/location_provider.dart';

class UserLocationMap extends StatefulWidget {
  const UserLocationMap({Key? key}) : super(key: key);

  @override
  _UserLocationMapState createState() => _UserLocationMapState();
}

class _UserLocationMapState extends State<UserLocationMap> {
  late GoogleMapController mapController;

  @override
  void initState() {
    super.initState();
    _getUserLocation();
  }

  Future<void> _getUserLocation() async {
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
    }
    if (permission == LocationPermission.deniedForever) {
      return;
    }
    Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high);

    final userLocation = LatLng(position.latitude, position.longitude);

    // Guardar la ubicación en el Provider
    Provider.of<LocationProvider>(context, listen: false)
        .setUserLocation(userLocation);

    // Mover la cámara si el mapa ya está creado
    if (mapController != null) {
      mapController.moveCamera(CameraUpdate.newLatLng(userLocation));
    }
  }

  @override
  Widget build(BuildContext context) {
    final userLocation = Provider.of<LocationProvider>(context).userLocation;

    return Container(
      height: 300,
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        boxShadow: const [
          BoxShadow(
            color: Colors.black26,
            blurRadius: 10,
            offset: Offset(0, 5),
          ),
        ],
      ),
      child: GoogleMap(
        onMapCreated: (GoogleMapController controller) {
          mapController = controller;
          if (userLocation != null) {
            mapController.moveCamera(CameraUpdate.newLatLng(userLocation));
          }
        },
        initialCameraPosition: CameraPosition(
          target: userLocation ??
              const LatLng(37.7749, -122.4194), // Coordenadas por defecto
          zoom: 15.0,
        ),
        myLocationEnabled: true,
      ),
    );
  }
}
