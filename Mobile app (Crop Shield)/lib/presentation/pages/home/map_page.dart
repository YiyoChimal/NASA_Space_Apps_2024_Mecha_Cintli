import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../widgets/seach_widget.dart';

class MapPage extends StatelessWidget {
  const MapPage({super.key});

  final greenAccent = const Color.fromRGBO(146, 172, 143, 0.41);
  final primaryGreen = const Color.fromRGBO(88, 144, 107, 1);
  final secondaryGreen = const Color.fromRGBO(146, 172, 143, 0.41);
  final hintColor = const Color.fromRGBO(121, 121, 121, 1);
  final backgroundColor = const Color.fromRGBO(255, 255, 255, 1);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: ListView(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Mapping your area',
                    style: GoogleFonts.firaSans(
                        fontSize: 30,
                        fontWeight: FontWeight.bold,
                        color: hintColor),
                  ),
                  IconButton(
                      onPressed: () {}, icon: const Icon(Icons.notifications))
                ],
              ),
              const SizedBox(height: 20),
              homeTextInput(),
              const SizedBox(height: 20),
              const Text('How does it works?',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  )),
              const SizedBox(height: 10),
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(20),
                    color: greenAccent),
                child: const Text(
                    'By signing up, your location is saved and the info is sent to the NASA data base where the coordinates are linked so that the user (you), can see the climate changes in you region. With this information, you might be able to know what to plant!'),
              ),
              const SizedBox(height: 70),
               const MapContainer(),
            ],
          ),
        ),
      ),
    );
  }
}


class MapContainer extends StatelessWidget {
   const MapContainer({
    super.key,
  });

  final greenAccent = const Color.fromRGBO(146, 172, 143, 0.41);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        color: greenAccent,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            margin: const EdgeInsets.all(10),
            child: const Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Link 1: URL...',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 5),
                Text(
                  'Link 2: URL...',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 5), 
                Text(
                  'Link 3: URL...',
                  style: TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10), // Added spacing before the image
          const Image(
            image: AssetImage('assets/images/mapa.png'),
            fit: BoxFit.cover,
            width: double.infinity,
          ),
        ],
      ),
    );
  }
}
