import 'package:flutter/material.dart';

SizedBox homeTextInput() {

    const greenAccent = Color.fromRGBO(146, 172, 143, 0.41);

    return SizedBox(
      height: 50,
      child: TextField(
        decoration: InputDecoration(
          hintText: 'Search info...',
          filled: true,
          fillColor: greenAccent,
          prefixIcon: const Icon(Icons.search),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(30),
          ),
        ),
      ),
    );
  }
