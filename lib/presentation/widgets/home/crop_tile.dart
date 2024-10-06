import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class CropTile extends StatelessWidget {
  const CropTile({
    super.key,
  });

final greenAccent = const Color.fromRGBO(146, 172, 143, 0.41);
final primaryGreen = const Color.fromRGBO(88, 144, 107, 1);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 100,
      margin: const EdgeInsets.only(bottom: 20),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(20),
        color: greenAccent,
      ),
      child: Row(
        children: [
          Container(
            width: 70,
            height: 70,
            margin: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(100),
              color: primaryGreen,
              image: const DecorationImage(
                image: AssetImage('assets/images/carrot.png'),
                fit: BoxFit.cover,
              ),
            ),
          ),
          const SizedBox(width: 20),
          Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Carrots',
                style: GoogleFonts.firaSans(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                'Season: Spring & Autumn',
                style: GoogleFonts.firaSans(
                  fontSize: 15,
                ),
              ),
            ],
          )
        ],
      ),
    );
  }
}
