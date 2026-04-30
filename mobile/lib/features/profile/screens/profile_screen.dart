import 'package:flutter/material.dart';
import 'package:viora_app/core/config/environment.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../../../core/l10n/locale_provider.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../../../core/routing/app_router.dart';
import '../../../shared/widgets/viora_card.dart';
import '../../../shared/widgets/viora_empty_state.dart';
import '../provider/profile_provider.dart';
import '../../auth/provider/auth_provider.dart';

/// Profile screen with avatar upload support.
class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _imagePicker = ImagePicker();

  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<ProfileProvider>().load());
  }

  Future<void> _pickAndUploadAvatar() async {
    final image = await _imagePicker.pickImage(
      source: ImageSource.gallery,
      maxWidth: 512,
      maxHeight: 512,
      imageQuality: 85,
    );
    if (image == null) return;

    final provider = context.read<ProfileProvider>();
    final success = await provider.uploadAvatar(image.path);

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(success
              ? AppLocalizations.of(context)!.profilePhotoUpdated
              : AppLocalizations.of(context)!.failedUploadPhoto),
          backgroundColor: success ? AppColors.success : AppColors.error,
        ),
      );
    }
  }

  void _showEditProfileDialog(
      BuildContext context, Map<String, dynamic>? profile) {
    final l10n = AppLocalizations.of(context)!;
    final nameCtrl = TextEditingController(text: profile?['full_name'] ?? '');
    final phoneCtrl =
        TextEditingController(text: profile?['phone_number'] ?? '');
    final bioCtrl = TextEditingController(text: profile?['bio'] ?? '');

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(l10n.editProfile),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Email (read-only)
              TextField(
                controller:
                    TextEditingController(text: profile?['email'] ?? ''),
                decoration: InputDecoration(
                  labelText: l10n.email,
                  prefixIcon: const Icon(Icons.email_outlined, size: 20),
                  enabled: false,
                ),
              ),
              const SizedBox(height: 12),
              // Full name
              TextField(
                controller: nameCtrl,
                decoration: InputDecoration(
                  labelText: l10n.fullName,
                  prefixIcon: const Icon(Icons.person_outline, size: 20),
                ),
              ),
              const SizedBox(height: 12),
              // Phone
              TextField(
                controller: phoneCtrl,
                keyboardType: TextInputType.phone,
                decoration: InputDecoration(
                  labelText: l10n.phoneNumber,
                  prefixIcon: const Icon(Icons.phone_outlined, size: 20),
                  hintText: '+966 5XX XXX XXXX',
                ),
              ),
              const SizedBox(height: 12),
              // Bio
              TextField(
                controller: bioCtrl,
                maxLines: 3,
                maxLength: 200,
                decoration: InputDecoration(
                  labelText: l10n.bio,
                  prefixIcon: const Padding(
                    padding: EdgeInsets.only(bottom: 40),
                    child: Icon(Icons.info_outline, size: 20),
                  ),
                  hintText: l10n.bioHint,
                  alignLabelWithHint: true,
                ),
              ),
              // Member since
              if (profile?['created_at'] != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.calendar_today_outlined,
                        size: 16, color: AppColors.textHint),
                    const SizedBox(width: 8),
                    Text(
                      '${l10n.memberSince} ${_formatDate(profile!['created_at'])}',
                      style: AppTextStyles.caption
                          .copyWith(color: AppColors.textHint),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx), child: Text(l10n.cancel)),
          ElevatedButton(
            onPressed: () async {
              final data = <String, dynamic>{
                'full_name': nameCtrl.text.trim(),
              };
              // Only include phone/bio if not empty
              final phone = phoneCtrl.text.trim();
              if (phone.isNotEmpty) data['phone_number'] = phone;
              final bio = bioCtrl.text.trim();
              data['bio'] = bio; // Allow clearing bio

              final success =
                  await context.read<ProfileProvider>().update(data);
              if (ctx.mounted) Navigator.pop(ctx);
              if (context.mounted) {
                final provider = context.read<ProfileProvider>();
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(success
                        ? l10n.profileUpdatedSuccess
                        : (provider.error ?? l10n.errorGeneric)),
                    backgroundColor:
                        success ? AppColors.success : AppColors.error,
                  ),
                );
              }
            },
            child: Text(l10n.saveChanges),
          ),
        ],
      ),
    );
  }

  String _formatDate(String isoDate) {
    try {
      final date = DateTime.parse(isoDate);
      return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
    } catch (_) {
      return isoDate;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppLocalizations.of(context)!.navProfile),
      ),
      body: Consumer<ProfileProvider>(
        builder: (_, provider, __) {
          if (provider.loading) {
            return const Center(
                child: CircularProgressIndicator(color: AppColors.primary));
          }

          if (provider.error != null && provider.profile == null) {
            return VioraEmptyState(
              icon: Icons.error_outline,
              title: provider.error!,
              actionLabel: AppLocalizations.of(context)!.retry,
              onAction: () => context.read<ProfileProvider>().load(),
            );
          }

          final profile = provider.profile;
          final avatarUrl = provider.avatarUrl;
          final name = profile?['full_name'] ?? '';
          final initial = name.isNotEmpty ? name[0].toUpperCase() : '?';

          return SingleChildScrollView(
            padding: AppSpacing.screenPadding,
            child: Column(
              children: [
                const SizedBox(height: 8),

                // ── Avatar hero section ──
                _AvatarHero(
                  name: name,
                  email: profile?['email'] ?? '',
                  initial: initial,
                  avatarUrl: avatarUrl,
                  uploading: provider.uploadingAvatar,
                  onTap: _pickAndUploadAvatar,
                ),
                const SizedBox(height: AppSpacing.sectionGap),

                // ── Settings tile group ──
                VioraCard(
                  padding: EdgeInsets.zero,
                  child: Column(
                    children: [
                      _SettingsItem(
                        icon: Icons.person_outline,
                        title: AppLocalizations.of(context)!.editProfile,
                        onTap: () => _showEditProfileDialog(context, profile),
                      ),
                      const Divider(height: 1, indent: 56),
                      _SettingsItem(
                        icon: Icons.language,
                        title: AppLocalizations.of(context)!.language,
                        onTap: () => _showLanguageDialog(context),
                      ),
                      const Divider(height: 1, indent: 56),
                      _SettingsItem(
                        icon: Icons.notifications_outlined,
                        title: AppLocalizations.of(context)!.notifications,
                        onTap: () => context.push(Routes.notifications),
                      ),
                      const Divider(height: 1, indent: 56),
                      _SettingsItem(
                        icon: Icons.info_outline,
                        title: AppLocalizations.of(context)!.about,
                        onTap: () {
                          final l10n = AppLocalizations.of(context)!;
                          showDialog(
                            context: context,
                            builder: (context) => AlertDialog(
                              title: Text(l10n.about),
                              content: Column(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  // شعار التطبيق أو أي أيقونة
                                  Image.asset('assets/logo.png',
                                    width: 80, 
                                    height: 80,
                                    fit: BoxFit.contain,
                                    ),
        
                                  const SizedBox(height: 16),

                                  // اسم التطبيق والنسخة
                                  Text(
                                    l10n.appName,
                                    style: AppTextStyles.h2
                                        .copyWith(color: AppColors.primary),
                                    textAlign: TextAlign.center,
                                  ),
                                  Text('Version 1.0.0',
                                      style: AppTextStyles.caption),

                                  const Divider(height: 32),

                                  // وصف التطبيق
                                  Text(
                                    l10n.appDescription,
                                    textAlign: TextAlign.center,
                                    style: AppTextStyles.body,
                                  ),

                                  const SizedBox(height: 16),

                                  // حقوق النشر
                                  Text(
                                    l10n.appCopyright,
                                    style: AppTextStyles.caption
                                        .copyWith(fontSize: 10),
                                    textAlign: TextAlign.center,
                                  ),
                                ],
                              ),
                              actions: [
                                TextButton(
                                  onPressed: () => Navigator.pop(context),
                                  child: Text(l10n.cancel), // أو "إغلاق"
                                ),
                              ],
                            ),
                          );
                        },
                        isLast: true,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: AppSpacing.sectionGap),

                Padding(
                  padding: const EdgeInsets.only(top: 24, bottom: 16),
                  child: Center(
                    child: Text(
                      AppLocalizations.of(context)!.appDeveloper,
                      style: const TextStyle(
                        fontSize: 11,
                        color: AppColors.textSecondary,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),

                // ── Logout ──
                SizedBox(
                  width: double.infinity,
                  height: 52,
                  child: OutlinedButton.icon(
                    onPressed: () async {
                      await context.read<AuthProvider>().logout();
                    },
                    icon: const Icon(Icons.logout,
                        color: AppColors.error, size: 20),
                    label: Text(
                      AppLocalizations.of(context)!.logout,
                      style:
                          AppTextStyles.button.copyWith(color: AppColors.error),
                    ),
                    style: OutlinedButton.styleFrom(
                      side: const BorderSide(color: AppColors.error),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(AppRadius.lg),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: AppSpacing.fabClearance),
              ],
            ),
          );
        },
      ),
    );
  }

  void _showLanguageDialog(BuildContext ctx) {
    showDialog(
      context: ctx,
      builder: (dialogCtx) {
        final localeProvider = ctx.read<LocaleProvider>();
        return SimpleDialog(
          title: Text(AppLocalizations.of(ctx)!.selectLanguageTitle),
          children: [
            RadioListTile<String>(
              title: Text(AppLocalizations.of(ctx)!.english),
              value: 'en',
              groupValue: localeProvider.locale.languageCode,
              onChanged: (v) {
                localeProvider.setLocale(const Locale('en'));
                Navigator.pop(dialogCtx);
                ScaffoldMessenger.of(ctx).showSnackBar(
                  SnackBar(
                      content: Text(
                          AppLocalizations.of(ctx)!.languageUpdatedSuccess)),
                );
              },
            ),
            RadioListTile<String>(
              title: Text(AppLocalizations.of(ctx)!.arabic),
              value: 'ar',
              groupValue: localeProvider.locale.languageCode,
              onChanged: (v) {
                localeProvider.setLocale(const Locale('ar'));
                Navigator.pop(dialogCtx);
                ScaffoldMessenger.of(ctx).showSnackBar(
                  SnackBar(
                      content: Text(
                          AppLocalizations.of(ctx)!.languageUpdatedSuccess)),
                );
              },
            ),
          ],
        );
      },
    );
  }
}

// ─── Sub-widgets ──────────────

class _AvatarHero extends StatelessWidget {
  final String name;
  final String email;
  final String initial;
  final String? avatarUrl;
  final bool uploading;
  final VoidCallback onTap;

  const _AvatarHero({
    required this.name,
    required this.email,
    required this.initial,
    this.avatarUrl,
    required this.uploading,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return VioraCard(
      color: AppColors.surfaceTinted,
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 20),
      child: Column(
        children: [
          // Avatar with upload tap
          GestureDetector(
            onTap: onTap,
            child: Stack(
              children: [
                Container(
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: AppColors.primary.withValues(alpha: 0.3),
                      width: 3,
                    ),
                  ),
                  child: CircleAvatar(
                    radius: 46,
                    backgroundColor: AppColors.primaryContainer,
                    backgroundImage: avatarUrl != null && avatarUrl!.isNotEmpty
                        ? NetworkImage("${Environment.apiBaseU}$avatarUrl")
                        : null,
                    child: avatarUrl == null || avatarUrl!.isEmpty
                        ? Text(initial,
                            style: AppTextStyles.h1.copyWith(
                                color: AppColors.primary, fontSize: 32))
                        : null,
                  ),
                ),
                Positioned(
                  bottom: 0,
                  right: 0,
                  child: Container(
                    width: 30,
                    height: 30,
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      shape: BoxShape.circle,
                      border: Border.all(color: AppColors.white, width: 2),
                    ),
                    child: uploading
                        ? const Padding(
                            padding: EdgeInsets.all(6),
                            child: CircularProgressIndicator(
                                strokeWidth: 2, color: AppColors.white),
                          )
                        : const Icon(Icons.camera_alt,
                            size: 14, color: AppColors.white),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          Text(name, style: AppTextStyles.h2.copyWith(fontSize: 22)),
          const SizedBox(height: 4),
          Text(email,
              style:
                  AppTextStyles.body.copyWith(color: AppColors.textSecondary)),
        ],
      ),
    );
  }
}

class _SettingsItem extends StatelessWidget {
  final IconData icon;
  final String title;
  final VoidCallback onTap;
  final bool isLast;

  const _SettingsItem({
    required this.icon,
    required this.title,
    required this.onTap,
    this.isLast = false,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: AppColors.primarySurface,
          borderRadius: BorderRadius.circular(AppRadius.sm),
        ),
        child: Icon(icon, color: AppColors.primary, size: 20),
      ),
      title: Text(title, style: AppTextStyles.body),
      trailing: Icon(
          Directionality.of(context) == TextDirection.rtl
              ? Icons.chevron_left
              : Icons.chevron_right,
          color: AppColors.textHint,
          size: 20),
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 2),
      onTap: onTap,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(
          top: isLast ? Radius.zero : Radius.zero,
          bottom: isLast ? const Radius.circular(16) : Radius.zero,
        ),
      ),
    );
  }
}
