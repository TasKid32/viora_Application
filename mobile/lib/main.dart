import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:go_router/go_router.dart';
import 'package:provider/provider.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/app_colors.dart';
import 'core/auth/token_manager.dart';
import 'core/api/api_client.dart';
import 'core/routing/app_router.dart';
import 'core/l10n/locale_provider.dart';
import 'features/auth/data/auth_api.dart';
import 'features/auth/provider/auth_provider.dart';
import 'features/analysis/data/analysis_api.dart';
import 'features/analysis/provider/analysis_provider.dart';
import 'features/dashboard/data/dashboard_api.dart';
import 'features/dashboard/provider/dashboard_provider.dart';
import 'features/roadmap/data/roadmap_api.dart';
import 'features/roadmap/provider/roadmap_provider.dart';
import 'features/chat/data/chat_api.dart';
import 'features/chat/provider/chat_provider.dart';
import 'features/profile/provider/profile_provider.dart';
import 'features/notifications/data/notification_api.dart';
import 'features/notifications/provider/notification_provider.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    debugPrint('❌ ${details.exceptionAsString()}');
  };

  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('❌ $error');
    return true;
  };

  runApp(const AppLoader());
}

class AppLoader extends StatefulWidget {
  const AppLoader({super.key});

  @override
  State<AppLoader> createState() => _AppLoaderState();
}

class _AppLoaderState extends State<AppLoader>
    with SingleTickerProviderStateMixin {

  bool _ready = false;

  late final AnimationController _pulseCtrl;
  late final Animation<double> _pulseAnimation;

  late final TokenManager _tokenManager;
  late final ApiClient _apiClient;
  late final AuthStateNotifier _authNotifier;
  late final GoRouter _router;
  late final LocaleProvider _localeProvider;

  @override
  void initState() {
    super.initState();

    // Logo breathing animation
    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    );

    _pulseAnimation = Tween<double>(
      begin: 0.92,
      end: 1.0,
    ).animate(
      CurvedAnimation(
        parent: _pulseCtrl,
        curve: Curves.easeInOut,
      ),
    );

    _pulseCtrl.repeat(reverse: true);

    _init();
  }

  Future<void> _init() async {

    _tokenManager = TokenManager();
    _localeProvider = LocaleProvider();

    await Future.wait([
      _tokenManager.init(),
      _localeProvider.init(),
    ]);

    _apiClient = ApiClient(_tokenManager);

    _authNotifier =
        AuthStateNotifier(_tokenManager.isAuthenticated);

    _apiClient.onForceLogout = () {
      _authNotifier.isAuthenticated = false;
    };

    _router = createRouter(
      authNotifier: _authNotifier,
    );
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {

    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 700),

      child: _ready

          // ================= MAIN APP =================

          ? VioraApp(
              key: const ValueKey('app'),
              tokenManager: _tokenManager,
              apiClient: _apiClient,
              authNotifier: _authNotifier,
              router: _router,
              localeProvider: _localeProvider,
            )

          // ================= SPLASH SCREEN =================

          : MaterialApp(
              debugShowCheckedModeBanner: false,
              theme: AppTheme.light,

              home: Scaffold(
                backgroundColor: Colors.white,

                body: SafeArea(
                  child: Container(

                    // Background gradient
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.topCenter,
                        end: Alignment.bottomCenter,
                        colors: [
                          Colors.white,
                          Color(0xFFF8F1FF),
                          Color(0xFFFDFBFF),
                        ],
                      ),
                    ),

                    child: Center(
                      child: AnimatedSlide(
                        duration:
                            const Duration(milliseconds: 900),

                        curve: Curves.easeOutBack,

                        offset: const Offset(0, 0),

                        child: AnimatedOpacity(
                          duration:
                              const Duration(milliseconds: 1200),

                          opacity: 1,

                          child: Column(
                            mainAxisSize: MainAxisSize.min,
                            children: [

                              // ================= LOGO =================

                              ScaleTransition(
                                scale: _pulseAnimation,

                                child: Container(
                                  width: 160,
                                  height: 160,

                                  decoration: BoxDecoration(
                                    shape: BoxShape.circle,

                                    boxShadow: [
                                      BoxShadow(
                                        color: AppColors.primary
                                            .withValues(alpha: 0.18),

                                        blurRadius: 40,
                                        offset:
                                            const Offset(0, 10),
                                      ),
                                    ],
                                  ),

                                  child: ClipOval(
                                    child: Image.asset(
                                      'assets/logo.png',
                                      fit: BoxFit.cover,
                                    ),
                                  ),
                                ),
                              ),

                              const SizedBox(height: 28),

                              // ================= APP NAME =================

                              RichText(
                                text: const TextSpan(
                                  children: [

                                    // vio
                                    TextSpan(
                                      text: 'vio',
                                      style: TextStyle(
                                        fontSize: 58,
                                        fontWeight:
                                            FontWeight.w900,
                                        color:
                                            Color(0xFF7B2CFF),
                                        letterSpacing: -2,
                                      ),
                                    ),

                                    // ra
                                    TextSpan(
                                      text: 'ra',
                                      style: TextStyle(
                                        fontSize: 58,
                                        fontWeight:
                                            FontWeight.w900,
                                        color:
                                            Color(0xFFFF4FB3),
                                        letterSpacing: -2,
                                      ),
                                    ),
                                  ],
                                ),
                              ),

                              const SizedBox(height: 18),

                              // ================= SLOGAN =================

                              Text(
                                'Together, we shape your future.',

                                style: TextStyle(
                                  fontSize: 17,

                                  color: AppColors.primary
                                      .withValues(alpha: 0.55),

                                  fontWeight: FontWeight.w500,
                                ),
                              ),

                              const SizedBox(height: 65),

                              // ================= BUTTON =================

                              Container(
                                width: 250,
                                height: 58,

                                decoration: BoxDecoration(
                                  gradient:
                                      AppColors.heroGradient,

                                  borderRadius:
                                      BorderRadius.circular(40),

                                  boxShadow: [
                                    BoxShadow(
                                      color: AppColors.primary
                                          .withValues(alpha: 0.25),

                                      blurRadius: 20,

                                      offset:
                                          const Offset(0, 8),
                                    ),
                                  ],
                                ),

                                child: ElevatedButton(
                                  style:
                                      ElevatedButton.styleFrom(
                                    backgroundColor:
                                        Colors.transparent,

                                    shadowColor:
                                        Colors.transparent,

                                    shape:
                                        RoundedRectangleBorder(
                                      borderRadius:
                                          BorderRadius.circular(
                                              40),
                                    ),
                                  ),

                                  onPressed: () {
                                    setState(
                                      () => _ready = true,
                                    );
                                  },

                                  child: const Text(
                                    'Get Started',

                                    style: TextStyle(
                                      fontSize: 18,
                                      fontWeight:
                                          FontWeight.w700,
                                    ),
                                  ),
                                ),
                              ),

                              const SizedBox(height: 120),

                              // ================= FOOTER =================

                              Text(
                                'Developed by Viora Team - Al-Jouf University ©2026',

                                textAlign: TextAlign.center,

                                style: TextStyle(
                                  fontSize: 12,

                                  color: const Color.fromARGB(255, 0, 0, 0)
                                      .withValues(alpha: 0.35),

                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),
                ),
              ),
            ),
    );
  }
}

class VioraApp extends StatelessWidget {

  final TokenManager tokenManager;
  final ApiClient apiClient;
  final AuthStateNotifier authNotifier;
  final GoRouter router;
  final LocaleProvider localeProvider;

  const VioraApp({
    super.key,
    required this.tokenManager,
    required this.apiClient,
    required this.authNotifier,
    required this.router,
    required this.localeProvider,
  });

  @override
  Widget build(BuildContext context) {

    return MultiProvider(
      providers: [

        ChangeNotifierProvider.value(
          value: localeProvider,
        ),

        ChangeNotifierProvider(
          create: (_) => AuthProvider(
            api: AuthApi(apiClient),
            tokenManager: tokenManager,
            authNotifier: authNotifier,
          ),
        ),

        ChangeNotifierProvider(
          create: (_) => AnalysisProvider(
            api: AnalysisApi(apiClient),
          ),
        ),

        ChangeNotifierProvider(
          create: (_) => DashboardProvider(
            api: DashboardApi(apiClient),
          ),
        ),

        ChangeNotifierProvider(
          create: (_) => RoadmapProvider(
            api: RoadmapApi(apiClient),
          ),
        ),

        ChangeNotifierProvider(
          create: (_) => ChatProvider(
            api: ChatApi(apiClient),
          ),
        ),

        ChangeNotifierProvider(
          create: (_) => ProfileProvider(
            api: apiClient,
          ),
        ),

        ChangeNotifierProvider(
          create: (_) => NotificationProvider(
            api: NotificationApi(apiClient),
          ),
        ),
      ],

      child: Consumer<LocaleProvider>(
        builder: (_, locale, __) => MaterialApp.router(

          title: 'Viora',
          debugShowCheckedModeBanner: false,

          theme: AppTheme.light,

          routerConfig: router,

          locale: locale.locale,

          supportedLocales: const [
            Locale('en'),
            Locale('ar'),
          ],

          localizationsDelegates: const [
            AppLocalizations.delegate,
            GlobalMaterialLocalizations.delegate,
            GlobalWidgetsLocalizations.delegate,
            GlobalCupertinoLocalizations.delegate,
          ],
        ),
      ),
    );
  }
}