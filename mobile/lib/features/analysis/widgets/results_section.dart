import 'package:flutter/material.dart';
import 'package:viora_app/l10n/app_localizations.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_styles.dart';
import '../../../core/routing/app_router.dart';
import '../../../shared/widgets/viora_card.dart';
import '../../../shared/widgets/viora_section_header.dart';
import '../provider/analysis_provider.dart';
import '../data/analysis_models.dart';
import '../../roadmap/provider/roadmap_provider.dart';
import '../../dashboard/provider/dashboard_provider.dart';

/// Results section — structured post-analysis view.
///
/// Layout order:
/// 1. Executive Summary (hero card)
/// 2. Top Strengths (capped + expandable)
/// 3. Skill Gaps (grouped + expandable)
/// 4. Recommendations (expandable)
/// 5. Job Opportunities (capped chips)
/// 6. Generate Roadmap CTA
class ResultsSection extends StatelessWidget {
  const ResultsSection({super.key});

  @override
  Widget build(BuildContext context) {
    final result = context.read<AnalysisProvider>().result;
    if (result == null) return const SizedBox.shrink();
    final l10n = AppLocalizations.of(context)!;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // ── 1. Executive Summary Card ──
        _ExecutiveSummary(result: result),
        const SizedBox(height: AppSpacing.sectionGap),

        // ── 2. CV Quality (if available) ──
        if (result.cvQuality != null) ...[
          _CvQualityCard(quality: result.cvQuality!),
          const SizedBox(height: AppSpacing.sectionGap),
        ],

        // ── 3. Top Strengths ──
        if (result.strongSkills.isNotEmpty) ...[
          VioraSectionHeader(
              title: l10n.strongSkills,
              icon: Icons.star,
              color: AppColors.success),
          const SizedBox(height: AppSpacing.itemGap),
          _ExpandableSkillList(
            skills: result.strongSkills,
            allSkills: result.extractedSkills,
            previewCount: 4,
          ),
          const SizedBox(height: AppSpacing.sectionGap),
        ],

        // ── 4. Skill Gaps ──
        if (result.missingSkills.isNotEmpty) ...[
          VioraSectionHeader(
              title: l10n.skillsToDevelop,
              icon: Icons.trending_up,
              color: AppColors.warning),
          const SizedBox(height: AppSpacing.itemGap),
          _ExpandableGapsList(skills: result.missingSkills, previewCount: 4),
          const SizedBox(height: AppSpacing.sectionGap),
        ],

        // ── 5. Recommendations ──
        if (result.recommendations.isNotEmpty) ...[
          VioraSectionHeader(
              title: l10n.recommendationsTitle,
              icon: Icons.lightbulb_outline,
              color: AppColors.primary),
          const SizedBox(height: AppSpacing.itemGap),
          _ExpandableRecommendations(
              items: result.recommendations, previewCount: 3),
          const SizedBox(height: AppSpacing.sectionGap),
        ],

        // ── 6. Languages ──
        if (result.languages.isNotEmpty) ...[
          VioraSectionHeader(
              title: l10n.languages,
              icon: Icons.language,
              color: AppColors.info),
          const SizedBox(height: AppSpacing.itemGap),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: result.languages
                .map((l) => Chip(
                      label: Text(l,
                          style: AppTextStyles.bodySmall
                              .copyWith(color: AppColors.primary)),
                      backgroundColor: AppColors.primarySurface,
                      side: BorderSide.none,
                      avatar: const Icon(Icons.translate,
                          size: 16, color: AppColors.primary),
                    ))
                .toList(),
          ),
          const SizedBox(height: AppSpacing.sectionGap),
        ],

        // ── 7. Job Opportunities ──
        if (result.jobOpportunities.isNotEmpty) ...[
          VioraSectionHeader(
              title: l10n.jobOpportunities,
              icon: Icons.work_outline,
              color: AppColors.info),
          const SizedBox(height: AppSpacing.itemGap),
          _ExpandableJobChips(jobs: result.jobOpportunities, previewCount: 4),
          const SizedBox(height: AppSpacing.sectionGap),
        ],

        // ── 8. Generate Roadmap CTA ──
        _GenerateRoadmapButton(analysisId: result.analysisId),
        const SizedBox(height: 72),
      ],
    );
  }
}

// ─── Executive Summary ─────────────────────────────────────

class _ExecutiveSummary extends StatelessWidget {
  final AnalysisResult result;
  const _ExecutiveSummary({required this.result});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final cvScore = (result.cvQuality?['quality_score'] as num?)?.toInt();

    return Container(
      width: double.infinity,
      padding: AppSpacing.cardPadding,
      decoration: BoxDecoration(
        gradient: AppColors.heroGradient,
        borderRadius: BorderRadius.circular(AppRadius.lg),
        boxShadow: const [
          BoxShadow(
              color: Color(0x307C3AED), blurRadius: 16, offset: Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(l10n.predictedCareer,
              style: AppTextStyles.bodySmall.copyWith(color: Colors.white70)),
          const SizedBox(height: 6),
          Text(result.predictedJob,
              style: AppTextStyles.h2.copyWith(color: Colors.white)),
          if (result.careerDirection.isNotEmpty) ...[
            const SizedBox(height: 6),
            Text(
              result.careerDirection,
              style: AppTextStyles.body.copyWith(color: Colors.white70),
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
          const SizedBox(height: 14),
          // Stat chips row
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _statChip(result.experienceLevel, Icons.badge_outlined),
              _statChip('${result.strongSkills.length} ${l10n.strongSkills}',
                  Icons.star_outline),
              if (result.missingSkills.isNotEmpty)
                _statChip(
                    '${result.missingSkills.length} ${l10n.skillsToDevelop}',
                    Icons.trending_up),
              if (cvScore != null)
                _statChip('CV $cvScore%', Icons.description_outlined),
            ],
          ),
        ],
      ),
    );
  }

  Widget _statChip(String text, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: Colors.white.withValues(alpha: 0.18),
        borderRadius: BorderRadius.circular(AppRadius.full),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: Colors.white),
          const SizedBox(width: 5),
          Text(text,
              style: AppTextStyles.caption
                  .copyWith(color: Colors.white, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }
}

// ─── Expandable Skill List (Strengths) ─────────────────────

class _ExpandableSkillList extends StatefulWidget {
  final List<Skill> skills;
  final List<String> allSkills;
  final int previewCount;
  const _ExpandableSkillList(
      {required this.skills, required this.allSkills, this.previewCount = 4});

  @override
  State<_ExpandableSkillList> createState() => _ExpandableSkillListState();
}

class _ExpandableSkillListState extends State<_ExpandableSkillList> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final visible = _expanded
        ? widget.skills
        : widget.skills.take(widget.previewCount).toList();
    final hasMore = widget.skills.length > widget.previewCount;

    return Column(
      children: [
        ...visible.map((s) => _SkillBar(skill: s)),
        if (hasMore)
          _ExpandButton(
            expanded: _expanded,
            totalCount: widget.skills.length,
            onTap: () => setState(() => _expanded = !_expanded),
          ),
        // "Show all extracted skills" — separate progressive disclosure
        if (widget.allSkills.length > widget.skills.length)
          Align(
            alignment: AlignmentDirectional.centerEnd,
            child: TextButton.icon(
              onPressed: () => _showAllSkills(context, widget.allSkills),
              icon: const Icon(Icons.expand_more, size: 16),
              label: Text(
                '${AppLocalizations.of(context)!.strongSkills} (${widget.allSkills.length})',
                style: AppTextStyles.caption.copyWith(color: AppColors.primary),
              ),
              style: TextButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                minimumSize: Size.zero,
                tapTargetSize: MaterialTapTargetSize.shrinkWrap,
              ),
            ),
          ),
      ],
    );
  }

  static void _showAllSkills(BuildContext context, List<String> skills) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (_) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(AppLocalizations.of(context)!.strongSkills,
                style: AppTextStyles.h3),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: skills
                  .map((s) => Chip(
                        label: Text(s, style: AppTextStyles.bodySmall),
                        backgroundColor: AppColors.primarySurface,
                        side: BorderSide.none,
                      ))
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }
}

// ─── Expandable Gaps List ──────────────────────────────────

class _ExpandableGapsList extends StatefulWidget {
  final List<MissingSkill> skills;
  final int previewCount;
  const _ExpandableGapsList({required this.skills, this.previewCount = 4});

  @override
  State<_ExpandableGapsList> createState() => _ExpandableGapsListState();
}

class _ExpandableGapsListState extends State<_ExpandableGapsList> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context)!;
    final visible = _expanded
        ? widget.skills
        : widget.skills.take(widget.previewCount).toList();
    final hasMore = widget.skills.length > widget.previewCount;

    // Group visible by type
    final tech = visible.where((s) => s.type == 'tech').toList();
    final hard = visible.where((s) => s.type == 'hard').toList();
    final soft = visible.where((s) => s.type == 'soft').toList();

    return Column(
      children: [
        if (tech.isNotEmpty)
          ..._buildSubGroup(
              tech, l10n.techSkills, Icons.build_outlined, AppColors.warning),
        if (hard.isNotEmpty)
          ..._buildSubGroup(
              hard, l10n.hardSkills, Icons.trending_up, AppColors.info),
        if (soft.isNotEmpty)
          ..._buildSubGroup(soft, l10n.softSkills, Icons.psychology_outlined,
              AppColors.success),
        if (hasMore)
          _ExpandButton(
            expanded: _expanded,
            totalCount: widget.skills.length,
            onTap: () => setState(() => _expanded = !_expanded),
          ),
      ],
    );
  }

  List<Widget> _buildSubGroup(
      List<MissingSkill> skills, String label, IconData icon, Color color) {
    return [
      Padding(
        padding: const EdgeInsets.only(top: 8, bottom: 8),
        child: Row(
          children: [
            Icon(icon, color: color, size: 16),
            const SizedBox(width: 6),
            Text(label,
                style: AppTextStyles.bodySmallBold.copyWith(color: color)),
            const SizedBox(width: 8),
            Expanded(
                child: Divider(
                    color: color.withValues(alpha: 0.15), thickness: 1)),
          ],
        ),
      ),
      ...skills.map((s) => _MissingSkillCard(skill: s)),
    ];
  }
}

// ─── Expandable Recommendations ────────────────────────────

class _ExpandableRecommendations extends StatefulWidget {
  final List<String> items;
  final int previewCount;
  const _ExpandableRecommendations(
      {required this.items, this.previewCount = 3});

  @override
  State<_ExpandableRecommendations> createState() =>
      _ExpandableRecommendationsState();
}

class _ExpandableRecommendationsState
    extends State<_ExpandableRecommendations> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final visible = _expanded
        ? widget.items
        : widget.items.take(widget.previewCount).toList();
    final hasMore = widget.items.length > widget.previewCount;

    return Column(
      children: [
        ...List.generate(
          visible.length,
          (i) => _RecommendationItem(text: visible[i], index: i + 1),
        ),
        if (hasMore)
          _ExpandButton(
            expanded: _expanded,
            totalCount: widget.items.length,
            onTap: () => setState(() => _expanded = !_expanded),
          ),
      ],
    );
  }
}

// ─── Expandable Job Chips ──────────────────────────────────

class _ExpandableJobChips extends StatefulWidget {
  final List<String> jobs;
  final int previewCount;
  const _ExpandableJobChips({required this.jobs, this.previewCount = 4});

  @override
  State<_ExpandableJobChips> createState() => _ExpandableJobChipsState();
}

class _ExpandableJobChipsState extends State<_ExpandableJobChips> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final visible = _expanded
        ? widget.jobs
        : widget.jobs.take(widget.previewCount).toList();
    final hasMore = widget.jobs.length > widget.previewCount;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: visible
              .map((j) => Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
                    decoration: BoxDecoration(
                      color: AppColors.primarySurface,
                      borderRadius: BorderRadius.circular(AppRadius.full),
                      border: Border.all(
                          color: AppColors.primary.withValues(alpha: 0.12)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.work_outline,
                            size: 14, color: AppColors.primary),
                        const SizedBox(width: 6),
                        Flexible(
                          child: Text(j,
                              style: AppTextStyles.bodySmall.copyWith(
                                color: AppColors.primary,
                                fontWeight: FontWeight.w600,
                              )),
                        ),
                      ],
                    ),
                  ))
              .toList(),
        ),
        if (hasMore)
          _ExpandButton(
            expanded: _expanded,
            totalCount: widget.jobs.length,
            onTap: () => setState(() => _expanded = !_expanded),
          ),
      ],
    );
  }
}

// ─── Shared Expand/Collapse Button ─────────────────────────

class _ExpandButton extends StatelessWidget {
  final bool expanded;
  final int totalCount;
  final VoidCallback onTap;

  const _ExpandButton(
      {required this.expanded, required this.totalCount, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: AlignmentDirectional.centerEnd,
      child: TextButton.icon(
        onPressed: onTap,
        icon: Icon(expanded ? Icons.expand_less : Icons.expand_more, size: 18),
        label: Text(
          expanded
              ? AppLocalizations.of(context)!.showLess
              : AppLocalizations.of(context)!.showAllCount(totalCount),
          style: AppTextStyles.caption.copyWith(color: AppColors.primary),
        ),
        style: TextButton.styleFrom(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          minimumSize: Size.zero,
          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
        ),
      ),
    );
  }
}

// ─── Generate Roadmap Button ───────────────────────────────

class _GenerateRoadmapButton extends StatefulWidget {
  final String analysisId;
  const _GenerateRoadmapButton({required this.analysisId});

  @override
  State<_GenerateRoadmapButton> createState() => _GenerateRoadmapButtonState();
}

class _GenerateRoadmapButtonState extends State<_GenerateRoadmapButton> {
  bool _generating = false;

  Future<void> _onPressed() async {
    if (_generating) return;

    final roadmapProvider = context.read<RoadmapProvider>();

    if (widget.analysisId.isEmpty) {
      context.go(Routes.roadmap);
      return;
    }

    setState(() => _generating = true);

    await roadmapProvider.generate(widget.analysisId);

    if (!mounted) return;
    setState(() => _generating = false);

    if (roadmapProvider.error != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
            content: Text(roadmapProvider.error!),
            backgroundColor: AppColors.error),
      );
    } else {
      try {
        context.read<DashboardProvider>().load();
      } catch (_) {}
      context.go(Routes.roadmap);
    }
  }

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 52,
      child: ElevatedButton.icon(
        onPressed: _generating ? null : _onPressed,
        icon: _generating
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(
                    strokeWidth: 2, color: AppColors.white))
            : const Icon(Icons.map_outlined),
        label: Text(_generating
            ? AppLocalizations.of(context)!.generatingPath
            : AppLocalizations.of(context)!.createLearningPath),
      ),
    );
  }
}

// ─── Sub-widgets ────────────────────────────────────────────

class _SkillBar extends StatelessWidget {
  final Skill skill;
  const _SkillBar({required this.skill});

  @override
  Widget build(BuildContext context) {
    final color = skill.proficiency >= 80
        ? AppColors.success
        : skill.proficiency >= 60
            ? AppColors.primary
            : AppColors.warning;

    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: VioraCard(
        color: AppColors.surfaceTinted,
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                // Skill icon badge
                Container(
                  width: 32,
                  height: 32,
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(AppRadius.sm),
                  ),
                  child: Icon(Icons.verified_outlined, color: color, size: 18),
                ),
                const SizedBox(width: 10),
                // Skill name
                Expanded(
                  child: Text(skill.name, style: AppTextStyles.bodyBold),
                ),
                // Proficiency badge
                Container(
                  width: 42,
                  height: 42,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: color.withValues(alpha: 0.08),
                    border: Border.all(
                        color: color.withValues(alpha: 0.3), width: 2),
                  ),
                  child: Center(
                    child: Text(
                      '${skill.proficiency}',
                      style: AppTextStyles.bodySmallBold
                          .copyWith(color: color, fontSize: 13),
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            // Full-width progress bar
            ClipRRect(
              borderRadius: BorderRadius.circular(3),
              child: LinearProgressIndicator(
                value: skill.proficiency / 100,
                minHeight: 4,
                backgroundColor: color.withValues(alpha: 0.08),
                valueColor: AlwaysStoppedAnimation(color),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MissingSkillCard extends StatelessWidget {
  final MissingSkill skill;
  const _MissingSkillCard({required this.skill});

  Color get _priorityColor {
    switch (skill.priority.toLowerCase()) {
      case 'high':
        return AppColors.error;
      case 'medium':
        return AppColors.warning;
      default:
        return AppColors.info;
    }
  }

  IconData get _typeIcon {
    switch (skill.type) {
      case 'tech':
        return Icons.code;
      case 'soft':
        return Icons.psychology_outlined;
      default:
        return Icons.trending_up;
    }
  }

  @override
  Widget build(BuildContext context) {
    final color = _priorityColor;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Container(
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(AppRadius.lg),
          border: Border.all(color: AppColors.outlineVariant),
        ),
        child: IntrinsicHeight(
          child: Row(
            children: [
              // Priority accent bar
              Container(
                width: 4,
                decoration: BoxDecoration(
                  color: color,
                  borderRadius: const BorderRadiusDirectional.only(
                    topStart: Radius.circular(AppRadius.lg),
                    bottomStart: Radius.circular(AppRadius.lg),
                  ),
                ),
              ),
              // Content
              Expanded(
                child: Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                  child: Row(
                    children: [
                      // Type icon
                      Container(
                        width: 30,
                        height: 30,
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.08),
                          borderRadius: BorderRadius.circular(AppRadius.sm),
                        ),
                        child: Icon(_typeIcon, color: color, size: 16),
                      ),
                      const SizedBox(width: 10),
                      // Name + reason
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(skill.skill, style: AppTextStyles.bodyBold),
                            if (skill.reason != null &&
                                skill.reason!.isNotEmpty)
                              Padding(
                                padding: const EdgeInsets.only(top: 3),
                                child: Text(
                                  skill.reason!,
                                  style: AppTextStyles.caption
                                      .copyWith(color: AppColors.textSecondary),
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      // Priority pill
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 10, vertical: 5),
                        decoration: BoxDecoration(
                          color: color.withValues(alpha: 0.08),
                          borderRadius: BorderRadius.circular(AppRadius.full),
                          border:
                              Border.all(color: color.withValues(alpha: 0.2)),
                        ),
                        child: Text(skill.priority,
                            style: AppTextStyles.caption.copyWith(
                                color: color,
                                fontWeight: FontWeight.w700,
                                fontSize: 11)),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _RecommendationItem extends StatelessWidget {
  final String text;
  final int index;
  const _RecommendationItem({required this.text, this.index = 0});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: VioraCard(
        padding: const EdgeInsets.all(14),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Number badge
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                color: AppColors.primary.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(AppRadius.sm),
              ),
              child: Center(
                child: Text(
                  '$index',
                  style: AppTextStyles.bodySmallBold
                      .copyWith(color: AppColors.primary, fontSize: 12),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                text,
                style: AppTextStyles.body.copyWith(height: 1.4),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _CvQualityCard extends StatelessWidget {
  final Map<String, dynamic> quality;
  const _CvQualityCard({required this.quality});

  @override
  Widget build(BuildContext context) {
    final score = (quality['quality_score'] as num?)?.toInt() ?? 0;
    final isValid = quality['is_valid'] as bool? ?? false;
    final wordCount = (quality['word_count'] as num?)?.toInt() ?? 0;
    final found = (quality['sections_found'] as List?)
            ?.map((s) => s.toString())
            .toList() ??
        [];
    final missing = (quality['sections_missing'] as List?)
            ?.map((s) => s.toString())
            .toList() ??
        [];
    final warnings =
        (quality['warnings'] as List?)?.map((s) => s.toString()).toList() ?? [];

    final Color scoreColor = score >= 70
        ? AppColors.success
        : (score >= 50 ? AppColors.warning : AppColors.error);
    final String scoreLabel = score >= 70
        ? AppLocalizations.of(context)!.excellent
        : (score >= 50
            ? AppLocalizations.of(context)!.acceptable
            : AppLocalizations.of(context)!.weak);

    return VioraCard(
      padding: const EdgeInsets.all(16),
      borderColor: scoreColor.withValues(alpha: 0.25),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(isValid ? Icons.verified : Icons.warning_amber,
                  color: scoreColor, size: 22),
              const SizedBox(width: 8),
              Text(AppLocalizations.of(context)!.resumeQuality,
                  style: AppTextStyles.h4),
              const Spacer(),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                decoration: BoxDecoration(
                  color: scoreColor.withValues(alpha: 0.08),
                  borderRadius: BorderRadius.circular(AppRadius.full),
                ),
                child: Text(
                  '$score% — $scoreLabel',
                  style:
                      AppTextStyles.bodySmallBold.copyWith(color: scoreColor),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: score / 100,
              minHeight: 6,
              backgroundColor: scoreColor.withValues(alpha: 0.08),
              valueColor: AlwaysStoppedAnimation(scoreColor),
            ),
          ),
          const SizedBox(height: 12),
          Text(AppLocalizations.of(context)!.wordsCount(wordCount),
              style: AppTextStyles.caption),
          if (found.isNotEmpty) ...[
            const SizedBox(height: 10),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: found
                  .map((s) =>
                      _sectionTag(s, AppColors.success, Icons.check_circle))
                  .toList(),
            ),
          ],
          if (missing.isNotEmpty) ...[
            const SizedBox(height: 6),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: missing
                  .map((s) => _sectionTag(s, AppColors.error, Icons.cancel))
                  .toList(),
            ),
          ],
          if (warnings.isNotEmpty) ...[
            const SizedBox(height: 10),
            ...warnings.map((w) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Icon(Icons.warning_amber,
                          size: 14, color: AppColors.warning),
                      const SizedBox(width: 6),
                      Expanded(
                        child: Text(w,
                            style: AppTextStyles.caption
                                .copyWith(color: AppColors.warning)),
                      ),
                    ],
                  ),
                )),
          ],
        ],
      ),
    );
  }

  Widget _sectionTag(String text, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.06),
        borderRadius: BorderRadius.circular(AppRadius.sm),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 4),
          Text(text,
              style:
                  AppTextStyles.caption.copyWith(color: color, fontSize: 11)),
        ],
      ),
    );
  }
}
