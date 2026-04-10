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

  // P2: Global error handler — catches widget build/layout/paint errors
  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    debugPrint('\u274c [FlutterError] ${details.exceptionAsString()}');
  };

  // P3: Custom error widget — show a friendly card instead of red crash screen
  ErrorWidget.builder = (FlutterErrorDetails details) {
    return Material(
      color: Colors.transparent,
      child: Center(
        child: Container(
          margin: const EdgeInsets.all(24),
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE53935), width: 1.5),
          ),
          child: const Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.warning_amber_rounded, size: 40, color: Color(0xFFE53935)),
              SizedBox(height: 12),
              Text(
                'Something went wrong',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              ),
              SizedBox(height: 4),
              Text(
                'Please restart the app or try again',
                style: TextStyle(fontSize: 13, color: Colors.grey),
              ),
            ],
          ),
        ),
      ),
    );
  };

  // P2b: Catch unhandled async errors (platform channel errors, etc.)
  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('\u274c [PlatformError] $error');
    return true; // Handled — prevent crash
  };

  runApp(const AppLoader());
}

/// Wrapper that initializes services, showing a branded loading screen,
/// then builds the real VioraApp once everything is ready.
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

    // Pulse animation for the logo (continuous breathing)
    _pulseCtrl = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    );
    _pulseAnimation = Tween<double>(begin: 0.88, end: 1.0).animate(
      CurvedAnimation(parent: _pulseCtrl, curve: Curves.easeInOut),
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
    _authNotifier = AuthStateNotifier(_tokenManager.isAuthenticated);

    _apiClient.onForceLogout = () {
      _authNotifier.isAuthenticated = false;
    };

    _router = createRouter(authNotifier: _authNotifier);

    if (mounted) setState(() => _ready = true);
  }

  @override
  void dispose() {
    _pulseCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 600),
      switchInCurve: Curves.easeOut,
      switchOutCurve: Curves.easeIn,
      child: _ready
          ? VioraApp(
              key: const ValueKey('app'),
              tokenManager: _tokenManager,
              apiClient: _apiClient,
              authNotifier: _authNotifier,
              router: _router,
              localeProvider: _localeProvider,
            )
          : MaterialApp(
              key: const ValueKey('splash'),
              debugShowCheckedModeBanner: false,
              theme: AppTheme.light,
              home: Scaffold(
                backgroundColor: AppColors.background,
                body: SafeArea(
                  child: Center(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        // Logo — ClipOval removes the square background edge
                        ScaleTransition(
                          scale: _pulseAnimation,
                          child: Container(
                            width: 140,
                            height: 140,
                            decoration: BoxDecoration(
                              shape: BoxShape.circle,
                              boxShadow: [
                                BoxShadow(
                                  color: AppColors.primary.withValues(alpha: 0.12),
                                  blurRadius: 30,
                                  offset: const Offset(0, 8),
                                ),
                              ],
                            ),
                            child: ClipOval(
                              child: Image.asset(
                                'assets/logo.png',
                                fit: BoxFit.cover,
                                width: 140,
                                height: 140,
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 20),

                        // App name — heroGradient for brand consistency
                        ShaderMask(
                          shaderCallback: (bounds) =>
                              AppColors.heroGradient.createShader(bounds),
                          child: const Text(
                            'Viora',
                            style: TextStyle(
                              fontSize: 34,
                              fontWeight: FontWeight.w800,
                              color: Colors.white,
                              letterSpacing: 1.5,
                            ),
                          ),
                        ),
                        const SizedBox(height: 32),

                        // Loading spinner — no text, spinner is sufficient
                        SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(
                            strokeWidth: 2.5,
                            color: AppColors.primary.withValues(alpha: 0.6),
                          ),
                        ),
                      ],
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
        ChangeNotifierProvider.value(value: localeProvider),
        ChangeNotifierProvider(
          create: (_) => AuthProvider(
            api: AuthApi(apiClient),
            tokenManager: tokenManager,
            authNotifier: authNotifier,
          ),
        ),
        ChangeNotifierProvider(
          create: (_) => AnalysisProvider(api: AnalysisApi(apiClient)),
        ),
        ChangeNotifierProvider(
          create: (_) => DashboardProvider(api: DashboardApi(apiClient)),
        ),
        ChangeNotifierProvider(
          create: (_) => RoadmapProvider(api: RoadmapApi(apiClient)),
        ),
        ChangeNotifierProvider(
          create: (_) => ChatProvider(api: ChatApi(apiClient)),
        ),
        ChangeNotifierProvider(
          create: (_) => ProfileProvider(api: apiClient),
        ),
        ChangeNotifierProvider(
          create: (_) => NotificationProvider(api: NotificationApi(apiClient)),
        ),
      ],
      child: Consumer<LocaleProvider>(
        builder: (_, locale, __) => MaterialApp.router(
          title: 'Viora',
          debugShowCheckedModeBanner: false,
          theme: AppTheme.light,
          routerConfig: router,
          locale: locale.locale,
          supportedLocales: const [Locale('en'), Locale('ar')],
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
