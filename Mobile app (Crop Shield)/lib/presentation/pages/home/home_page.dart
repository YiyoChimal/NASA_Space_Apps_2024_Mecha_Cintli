import 'package:crop_shield/presentation/widgets/home/crop_tile.dart';
import 'package:crop_shield/presentation/widgets/home/disaster_card.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import '../../widgets/seach_widget.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  State<HomePage> createState() => _HomePageState();
}

class _HomePageState extends State<HomePage> {
  final greenAccent = const Color.fromRGBO(146, 172, 143, 0.41);
  final primaryGreen = const Color.fromRGBO(88, 144, 107, 1);
  final hintColor = const Color.fromRGBO(121, 121, 121, 1);
  final backgroundColor = const Color.fromRGBO(255, 255, 255, 1);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: backgroundColor,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Home',
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
              Text('Natural disasters',
                  style: GoogleFonts.firaSans(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      color: hintColor)),
              const SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    DisasterCard(title: 'Flood', path: 'assets/images/flood.png'),
                    DisasterCard(title: 'Droughts', path: 'assets/images/dis2.png'),
                    DisasterCard(title: 'Snowfallen', path: 'assets/images/dis3.png'),
                    DisasterCard(title: 'Hurricane', path: 'assets/images/dis4.png'),
                    DisasterCard(title: 'Tornado', path: 'assets/images/dis5.png'),
                  ],
                ),
              ),
              const SizedBox(height: 20),
              const Text(
                'Crops to plant',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Expanded(
                child: ListView(
                  shrinkWrap: true,
                  children: const [
                    CropTile(title: 'Carrot', path: 'assets/images/carrot.png',),
                    CropTile(title: 'Corn', path: 'assets/images/corn.png',),
                    CropTile(title: 'Leather', path: 'assets/images/leather.png',),
                    CropTile(title: 'Cotton', path: 'assets/images/cotton.png',),
                    CropTile(title: 'Potato', path: 'assets/images/potato.png',),
                  ],
                ),
              )
            ],
          ),
        ),
      ),
    );
  }

  
}
