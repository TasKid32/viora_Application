import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../../../core/routing/app_router.dart';
import '../provider/auth_provider.dart';
import '../widgets/auth_text_field.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  bool _obscurePassword = true;

  @override
  void dispose() {
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    final auth = context.read<AuthProvider>();
    final success = await auth.login(
      email: _emailCtrl.text.trim(),
      password: _passwordCtrl.text,
    );

    if (success && mounted) {}
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;

    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // ------------------ محتوى الشاشة ------------------
            Expanded(
              child: SingleChildScrollView(
                padding: AppSpacing.screenPadding,
                child: Form(
                  key: _formKey,
                  child: Column(
                    children: <Widget>[
                      const SizedBox(height: 40),

                      // Logo
                      Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          color: AppColors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: AppColors.primary.withValues(alpha: 0.2),
                              blurRadius: 20,
                              offset: const Offset(0, 8),
                            ),
                          ],
                        ),
                        child: ClipOval(
                          child: Image.asset(
                            'assets/logo.png',
                            width: 60,
                            height: 60,
                          ),
                        ),
                      ),
                      const SizedBox(height: 24),

                      // Title
                      Row(
                         mainAxisAlignment: MainAxisAlignment.center,
                        crossAxisAlignment: CrossAxisAlignment.end,
                       children: [
    // Welcome To
    Text(
      AppLocalizations.of(context)!.welcomeBack,
      style: TextStyle(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: AppColors.primary,
      ),
    ),

    const SizedBox(width: 6),

    // VIORA (Gradient)
    ShaderMask(
      shaderCallback: (bounds) => LinearGradient(
        colors: [
          Color(0xFF8E24AA), // Purple
          Color(0xFFE91E63), // Pink
          Color(0xFFF48FB1), // Light Pink
        ],
      ).createShader(bounds),
      child: Text(
        AppLocalizations.of(context)!.viora,
        style: TextStyle(
          fontSize: 30,
          fontWeight: FontWeight.bold,
          color: Colors.white,
        ),
      ),
    ),
  ],
),
                          
                      Text(
                        l10n.signInToContinue,
                        style: AppTextStyles.body.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 40),

                      // Error message
                      Selector<AuthProvider, String?>(
                        selector: (_, p) => p.error,
                        builder: (_, error, __) {
                          if (error == null) return const SizedBox.shrink();
                          return Container(
                            width: double.infinity,
                            padding: const EdgeInsets.all(12),
                            margin: const EdgeInsets.only(bottom: 16),
                            decoration: BoxDecoration(
                              color: AppColors.error.withValues(alpha: 0.1),
                              borderRadius:
                                  BorderRadius.circular(AppRadius.md),
                              border: Border.all(
                                color: AppColors.error.withValues(alpha: 0.3),
                              ),
                            ),
                            child: Text(
                              error,
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.error,
                              ),
                            ),
                          );
                        },
                      ),

                      // Email
                      AuthTextField(
                        controller: _emailCtrl,
                        label: l10n.email,
                        hint: l10n.emailHint,
                        icon: Icons.email_outlined,
                        keyboardType: TextInputType.emailAddress,
                        validator: (v) {
                          if (v == null || v.isEmpty) {
                            return l10n.pleaseEnterEmail;
                          }
                          if (!v.contains('@')) {
                            return l10n.pleaseEnterValidEmail;
                          }
                          return null;
                        }, errorMaxLines: 2,
                      ),
                      const SizedBox(height: 16),

                      // Password
                      AuthTextField(
                        controller: _passwordCtrl,
                        label: l10n.password,
                        hint: '••••••••',
                        icon: Icons.lock_outline,
                        obscure: _obscurePassword,
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscurePassword
                                ? Icons.visibility_off_outlined
                                : Icons.visibility_outlined,
                            color: AppColors.textHint,
                          ),
                          onPressed: () => setState(
                            () => _obscurePassword = !_obscurePassword,
                          ),
                        ),
                        validator: (v) {
                          if (v == null || v.isEmpty) {
                            return l10n.pleaseEnterPassword;
                          }
                          if (v.length < 6) return l10n.passwordMinLength;
                          return null;
                        }, errorMaxLines: 2,
                      ),
                      const SizedBox(height: 12),

                      // Forgot Password
                      Align(
                        alignment: AlignmentDirectional.centerEnd,
                        child: TextButton(
                          onPressed: () => context.go(Routes.forgotPassword),
                          child: Text(
                            l10n.forgotPasswordTitle,
                            style: AppTextStyles.bodySmall.copyWith(
                              color: AppColors.primary,
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),

                      // Login button
                      Selector<AuthProvider, bool>(
                        selector: (_, p) => p.loading,
                        builder: (_, loading, __) {
                          return ElevatedButton(
                            onPressed: loading ? null : _handleLogin,
                            child: loading
                                ? const SizedBox(
                                    width: 24,
                                    height: 24,
                                    child: CircularProgressIndicator(
                                      color: AppColors.white,
                                      strokeWidth: 2,
                                    ),
                                  )
                                : Text(l10n.signIn),
                          );
                        },
                      ),
                      const SizedBox(height: 20),

                      // Register link
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            l10n.dontHaveAccount,
                            style: AppTextStyles.body.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                          TextButton(
                            onPressed: () => context.go(Routes.register),
                            child: Text(l10n.signUp),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),

            // ------------------ سطر الحقوق ------------------
            Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: Text(
                AppLocalizations.of(context)!.appDeveloper,
                style: const TextStyle(
                  fontSize: 11,
                  color: AppColors.textSecondary,
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
