import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../../../core/routing/app_router.dart';
import '../provider/auth_provider.dart';
import '../widgets/auth_text_field.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _emailCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _confirmCtrl = TextEditingController();
  bool _obscurePassword = true;
  bool _obscureConfirm = true;

  @override
  void dispose() {
    _nameCtrl.dispose();
    _emailCtrl.dispose();
    _passwordCtrl.dispose();
    _confirmCtrl.dispose();
    super.dispose();
  }

  Future<void> _handleRegister() async {
    if (!_formKey.currentState!.validate()) return;

    final auth = context.read<AuthProvider>();
    final success = await auth.register(
      name: _nameCtrl.text.trim(),
      email: _emailCtrl.text.trim(),
      password: _passwordCtrl.text,
      confirmPassword: _confirmCtrl.text,
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
                    children: [
                      const SizedBox(height: 30),

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
                          child: Image.asset('assets/logo.png',
                              width: 60, height: 60),
                        ),
                      ),
                      const SizedBox(height: 20),

                      Text(
                        l10n.createAccount,
                        style: AppTextStyles.h1.copyWith(
                          color: AppColors.primary,
                           fontSize: 30,
                           fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),

                      Text(
                        l10n.startCareerJourney,
                        style: AppTextStyles.body.copyWith(
                          color: AppColors.textSecondary,
                        ),
                      ),
                      const SizedBox(height: 30),

                      // Error
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
                              borderRadius: BorderRadius.circular(AppRadius.md),
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

                      // Name
                      AuthTextField(
                        controller: _nameCtrl,
                        label: l10n.fullName,
                        hint: l10n.fullNameHint,
                        icon: Icons.person_outline,
                        validator: (v) => (v == null || v.isEmpty)
                            ? l10n.pleaseEnterName
                            : null,
                        errorMaxLines: 2,
                      ),
                      const SizedBox(height: 14),

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
                        },
                        errorMaxLines: 2,
                      ),
                      const SizedBox(height: 14),

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
                          // Minimum 8 characters, at least one uppercase letter, one lowercase letter and one number,
                          if (!RegExp(
                                  r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*])')
                              .hasMatch(v)) {
                            return l10n.passwordMinLength;
                          }
                          return null;
                        },
                        errorMaxLines: 2,
                      ),
                      const SizedBox(height: 14),

                      // Confirm password
                      AuthTextField(
                        controller: _confirmCtrl,
                        label: l10n.confirmPassword,
                        hint: '••••••••',
                        icon: Icons.lock_outline,
                        obscure: _obscureConfirm,
                        suffixIcon: IconButton(
                          icon: Icon(
                            _obscureConfirm
                                ? Icons.visibility_off_outlined
                                : Icons.visibility_outlined,
                            color: AppColors.textHint,
                          ),
                          onPressed: () => setState(
                            () => _obscureConfirm = !_obscureConfirm,
                          ),
                        ),
                        validator: (v) {
                          if (v == null || v.isEmpty) {
                            return l10n.pleaseConfirmPassword;
                          }
                          if (v != _passwordCtrl.text) {
                            return l10n.passwordsDoNotMatch;
                          }
                          return null;
                        },
                        errorMaxLines: 4,
                      ),
                      const SizedBox(height: 28),

                      // Register button
                      Selector<AuthProvider, bool>(
                        selector: (_, p) => p.loading,
                        builder: (_, loading, __) {
                          return ElevatedButton(
                            onPressed: loading ? null : _handleRegister,
                            child: loading
                                ? const SizedBox(
                                    width: 24,
                                    height: 24,
                                    child: CircularProgressIndicator(
                                      color: AppColors.white,
                                      strokeWidth: 2,
                                    ),
                                  )
                                : Text(l10n.createAccount),
                          );
                        },
                      ),
                      const SizedBox(height: 16),

                      // Login link
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            l10n.alreadyHaveAccount,
                            style: AppTextStyles.body.copyWith(
                              color: AppColors.textSecondary,
                            ),
                          ),
                          TextButton(
                            onPressed: () => context.go(Routes.login),
                            child: Text(l10n.signIn),
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
