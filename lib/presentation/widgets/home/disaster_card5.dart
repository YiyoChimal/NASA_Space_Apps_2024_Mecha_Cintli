import 'package:flutter/material.dart';

class DisasterCard5 extends StatelessWidget {
  const DisasterCard5({super.key, this.title});

  final String? title;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 170,
      margin: const EdgeInsets.only(right: 5),
      child: Card(
        color: const Color.fromRGBO(71, 133, 92, 0.91),
        child: Column(
          children: [
            const Image(
              image: AssetImage('assets/images/dis5.png'),
            ),
            Container(
                decoration: BoxDecoration(
                  color: const Color.fromRGBO(44, 88, 59, 1.91),
                  borderRadius: BorderRadius.circular(5),
                ),
                child:  Text(title ?? 'Cyclone')),
          ],
        ),
      ),
    );
  }
}