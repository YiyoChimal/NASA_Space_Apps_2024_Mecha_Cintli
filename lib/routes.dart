import 'package:crop_shield/presentation/pages/home/home_page.dart';
import 'package:crop_shield/presentation/pages/auth/login_page.dart';
import 'package:crop_shield/presentation/pages/auth/sign_up.page.dart';
import 'package:crop_shield/presentation/pages/splash_page.dart';
import 'package:go_router/go_router.dart';

final GoRouter router = GoRouter(
  routes: [
    
    GoRoute(path: '/', builder: (context, state) =>  SplashPage(),),
    GoRoute(path: '/login', builder: (context, state) =>  LoginPage(),),
    GoRoute(path: '/sign_up', builder: (context, state) =>  SignUpPage(),),
    GoRoute(path: '/home', builder: (context, state) =>  HomePage(),),
  ]
);
    