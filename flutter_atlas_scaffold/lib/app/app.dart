import 'package:flutter/material.dart';

import 'routes.dart';

class AtlasDialApp extends StatelessWidget {
  const AtlasDialApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Atlas Dial Core',
      theme: ThemeData.dark(useMaterial3: true),
      routes: AppRoutes.map,
      initialRoute: AppRoutes.dial,
    );
  }
}

