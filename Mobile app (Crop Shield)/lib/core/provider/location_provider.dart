import 'package:flutter/foundation.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';

class LocationProvider with ChangeNotifier {
  LatLng? _userLocation;

  LatLng? get userLocation => _userLocation;

  void setUserLocation(LatLng location) {
    _userLocation = location;
    notifyListeners();
  }
}
