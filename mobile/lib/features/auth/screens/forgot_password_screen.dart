import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:dio/dio.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../../../core/routing/app_router.dart';
import '../../../core/utils/error_helper.dart';
import '../widgets/auth_text_field.dart';
import '../provider/auth_provider.dart';

/// Forgot Password screen — two phases: enter email → confirmation.
class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailCtrl = TextEditingController();
  bool _loading = false;
  bool _sent = false;
  String? _error;

  @override
  void dispose() {
    _emailCtrl.dispose();
    super.dispose();
  }

  Future<void> _handleSend() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final authProvider = context.read<AuthProvider>();
      await authProvider.api.forgotPassword(_emailCtrl.text.trim());

      if (mounted) {
        setState(() {
          _sent = true;
          _loading = false;
        });
      }
    } on DioException catch (e) {
      if (mounted) {
        setState(() {
          _error = extractDioError(e);
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = AppLocalizations.of(context)!.errorUnknown;
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: AppSpacing.screenPadding,
          child: _sent ? _buildConfirmation() : _buildForm(),
        ),
      ),
    );
  }

  Widget _buildForm() {
    final l10n = AppLocalizations.of(context)!;
    return Form(
      key: _formKey,
      child: Column(
        children: [
          const SizedBox(height: 40),

          // Back button
          Align(
            alignment: AlignmentDirectional.centerStart,
            child: IconButton(
              onPressed: () => context.go(Routes.login),
              icon: const Icon(Icons.arrow_back, color: AppColors.textPrimary),
            ),
          ),
          const SizedBox(height: 16),

          // Icon
          Container(
            width: 80,
            height: 80,
            decoration: BoxDecoration(
              color: AppColors.primarySurface,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.lock_reset,
                size: 40, color: AppColors.primary),
          ),
          const SizedBox(height: 24),

          // Title
          Text(
            l10n.forgotPasswordTitle,
            style: AppTextStyles.h1.copyWith(color: AppColors.primary),
          ),
          const SizedBox(height: 8),
          Text(
            l10n.forgotPasswordDescription,
            style: AppTextStyles.body.copyWith(color: AppColors.textSecondary),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 40),

          // Error
          if (_error != null)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: AppColors.error.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(AppRadius.md),
                border:
                    Border.all(color: AppColors.error.withValues(alpha: 0.3)),
              ),
              child: Text(_error!,
                  style:
                      AppTextStyles.bodySmall.copyWith(color: AppColors.error)),
            ),

          // Email field
          AuthTextField(
            controller: _emailCtrl,
            label: l10n.emailAddress,
            hint: l10n.emailHint,
            icon: Icons.email_outlined,
            keyboardType: TextInputType.emailAddress,
            validator: (v) {
              if (v == null || v.isEmpty) return l10n.pleaseEnterEmail;
              if (!v.contains('@')) return l10n.pleaseEnterValidEmail;
              return null;
            }, errorMaxLines: 2,
          ),
          const SizedBox(height: 32),

          // Send button
          ElevatedButton(
            onPressed: _loading ? null : _handleSend,
            child: _loading
                ? const SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                        color: AppColors.white, strokeWidth: 2),
                  )
                : Text(l10n.sendResetLink),
          ),
          const SizedBox(height: 20),

          // Back to login
          TextButton(
            onPressed: () => context.go(Routes.login),
            child: Text(
              l10n.backToSignIn,
              style: AppTextStyles.body.copyWith(color: AppColors.primary),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConfirmation() {
    final l10n = AppLocalizations.of(context)!;
    return Column(
      children: [
        const SizedBox(height: 80),

        // Success icon
        Container(
          width: 100,
          height: 100,
          decoration: BoxDecoration(
            color: AppColors.success.withValues(alpha: 0.1),
            shape: BoxShape.circle,
          ),
          child: const Icon(Icons.mark_email_read,
              size: 48, color: AppColors.success),
        ),
        const SizedBox(height: 24),

        Text(
          l10n.checkYourEmail,
          style: AppTextStyles.h1.copyWith(color: AppColors.primary),
        ),
        const SizedBox(height: 12),
        Text(
          l10n.resetLinkSent,
          style: AppTextStyles.body.copyWith(color: AppColors.textSecondary),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),
        Text(
          _emailCtrl.text.trim(),
          style: AppTextStyles.bodyBold.copyWith(color: AppColors.textPrimary),
        ),
        const SizedBox(height: 32),

        // Hint
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.primarySurface,
            borderRadius: BorderRadius.circular(AppRadius.md),
          ),
          child: Column(
            children: [
              Text(
                l10n.didntReceiveEmail,
                style: AppTextStyles.bodyBold
                    .copyWith(color: AppColors.textPrimary),
              ),
              const SizedBox(height: 4),
              Text(
                l10n.checkSpamOrRetry,
                style:
                    AppTextStyles.bodySmall.copyWith(color: AppColors.textHint),
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),

        // Resend
        OutlinedButton(
          onPressed: () {
            setState(() {
              _sent = false;
              _error = null;
            });
          },
          style: OutlinedButton.styleFrom(
            side: const BorderSide(color: AppColors.primary),
            minimumSize: const Size(double.infinity, 52),
          ),
          child: Text(
            l10n.resendEmail,
            style: AppTextStyles.button.copyWith(color: AppColors.primary),
          ),
        ),
        const SizedBox(height: 16),

        // Back to login
        ElevatedButton(
          onPressed: () => context.go(Routes.login),
          child: Text(l10n.backToSignIn),
        ),
      ],
    );
  }
}
