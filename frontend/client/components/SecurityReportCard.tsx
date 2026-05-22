import React, { useState } from "react";
import { Card } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  ShieldAlert,
  ShieldCheck,
  ShieldX,
  ChevronDown,
  ChevronUp,
  FileWarning,
  AlertTriangle,
  Info,
  Lock,
} from "lucide-react";

// ─── Types ───────────────────────────────────────────────────────────────────

interface SecurityFinding {
  severity: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW";
  rule_id: string;
  description: string;
  file_path: string;
  line_number: number;
  redacted_snippet: string;
  recommendation: string;
}

interface SecurityReport {
  scanned_files: number;
  scan_duration_ms: number;
  findings: SecurityFinding[];
  severity_counts: Record<string, number>;
  is_clean: boolean;
  blocked: boolean;
  summary: string;
}

interface SecurityReportCardProps {
  report: SecurityReport;
  className?: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

const SEVERITY_CONFIG = {
  CRITICAL: {
    label: "Critical",
    badgeCls:
      "bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800/50",
    rowCls:
      "border-red-200 dark:border-red-800/40 bg-red-50/60 dark:bg-red-900/10",
    icon: ShieldX,
    iconCls: "text-red-500",
    dot: "bg-red-500",
  },
  HIGH: {
    label: "High",
    badgeCls:
      "bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-800/50",
    rowCls:
      "border-orange-200 dark:border-orange-800/40 bg-orange-50/60 dark:bg-orange-900/10",
    icon: AlertTriangle,
    iconCls: "text-orange-500",
    dot: "bg-orange-500",
  },
  MEDIUM: {
    label: "Medium",
    badgeCls:
      "bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/30 dark:text-amber-400 dark:border-amber-800/50",
    rowCls:
      "border-amber-200 dark:border-amber-800/40 bg-amber-50/40 dark:bg-amber-900/10",
    icon: FileWarning,
    iconCls: "text-amber-500",
    dot: "bg-amber-500",
  },
  LOW: {
    label: "Low",
    badgeCls:
      "bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800/50",
    rowCls:
      "border-blue-200 dark:border-blue-800/40 bg-blue-50/40 dark:bg-blue-900/10",
    icon: Info,
    iconCls: "text-blue-500",
    dot: "bg-blue-400",
  },
} as const;

// ─── Sub-components ───────────────────────────────────────────────────────────

function FindingRow({ finding }: { finding: SecurityFinding }) {
  const [open, setOpen] = useState(false);
  const cfg = SEVERITY_CONFIG[finding.severity] ?? SEVERITY_CONFIG.LOW;
  const Icon = cfg.icon;

  return (
    <div
      className={cn(
        "rounded-xl border transition-all duration-200",
        cfg.rowCls,
      )}
    >
      {/* Collapsed row */}
      <button
        onClick={() => setOpen((o) => !o)}
        className="w-full flex items-start gap-3 p-3 text-left group"
        aria-expanded={open}
      >
        <span className={cn("mt-0.5 flex-shrink-0", cfg.iconCls)}>
          <Icon className="w-4 h-4" />
        </span>

        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2 mb-0.5">
            <Badge
              variant="outline"
              className={cn("text-[9px] font-black uppercase tracking-wider px-1.5 py-0", cfg.badgeCls)}
            >
              {cfg.label}
            </Badge>
            <span className="text-xs font-bold text-slate-800 dark:text-slate-200 truncate">
              {finding.description}
            </span>
          </div>
          <span className="text-[11px] font-mono text-slate-500 dark:text-slate-400 truncate block">
            {finding.file_path}
            {finding.line_number > 0 && (
              <span className="text-slate-400 dark:text-slate-600">
                {" "}
                : line {finding.line_number}
              </span>
            )}
          </span>
        </div>

        <span className="flex-shrink-0 text-slate-400 group-hover:text-slate-600 dark:group-hover:text-slate-300 transition-colors mt-0.5">
          {open ? (
            <ChevronUp className="w-4 h-4" />
          ) : (
            <ChevronDown className="w-4 h-4" />
          )}
        </span>
      </button>

      {/* Expanded detail */}
      {open && (
        <div className="px-4 pb-4 space-y-3 border-t border-inherit pt-3">
          {/* Redacted snippet */}
          <div>
            <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-1">
              Detected Snippet
            </p>
            <pre className="text-[11px] font-mono text-slate-700 dark:text-slate-300 bg-slate-900/5 dark:bg-slate-950/60 px-3 py-2 rounded-lg overflow-x-auto whitespace-pre-wrap break-all border border-slate-200 dark:border-slate-800">
              {finding.redacted_snippet}
            </pre>
          </div>

          {/* Recommendation */}
          <div className="flex gap-2 items-start bg-white dark:bg-slate-900/60 rounded-lg px-3 py-2.5 border border-slate-200 dark:border-slate-700/50">
            <Lock className="w-3.5 h-3.5 text-slate-400 mt-0.5 flex-shrink-0" />
            <div>
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-0.5">
                Remediation
              </p>
              <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed">
                {finding.recommendation}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Main Card ────────────────────────────────────────────────────────────────

export default function SecurityReportCard({
  report,
  className,
}: SecurityReportCardProps) {
  const [expanded, setExpanded] = useState(!report.is_clean);

  const headerCls = report.blocked
    ? "bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800/50"
    : report.is_clean
      ? "bg-emerald-50 dark:bg-emerald-950/30 border-emerald-200 dark:border-emerald-800/50"
      : "bg-amber-50 dark:bg-amber-950/30 border-amber-200 dark:border-amber-800/50";

  const HeaderIcon = report.blocked
    ? ShieldX
    : report.is_clean
      ? ShieldCheck
      : ShieldAlert;

  const headerIconCls = report.blocked
    ? "text-red-500"
    : report.is_clean
      ? "text-emerald-500"
      : "text-amber-500";

  const titleCls = report.blocked
    ? "text-red-700 dark:text-red-400"
    : report.is_clean
      ? "text-emerald-700 dark:text-emerald-400"
      : "text-amber-700 dark:text-amber-400";

  const counts = report.severity_counts ?? {};
  const totalFindings = report.findings?.length ?? 0;

  return (
    <Card
      className={cn(
        "overflow-hidden border shadow-sm",
        report.blocked
          ? "border-red-200 dark:border-red-800/50"
          : report.is_clean
            ? "border-emerald-200 dark:border-emerald-800/50"
            : "border-amber-200 dark:border-amber-800/50",
        className,
      )}
    >
      {/* ── Header ── */}
      <div
        className={cn(
          "flex items-center justify-between gap-3 px-4 py-3 border-b cursor-pointer select-none",
          headerCls,
        )}
        onClick={() => setExpanded((e) => !e)}
        role="button"
        aria-expanded={expanded}
      >
        <div className="flex items-center gap-3">
          <div
            className={cn(
              "w-8 h-8 rounded-lg flex items-center justify-center",
              report.blocked
                ? "bg-red-100 dark:bg-red-900/40"
                : report.is_clean
                  ? "bg-emerald-100 dark:bg-emerald-900/40"
                  : "bg-amber-100 dark:bg-amber-900/40",
            )}
          >
            <HeaderIcon className={cn("w-4 h-4", headerIconCls)} />
          </div>

          <div>
            <h3 className={cn("text-sm font-extrabold", titleCls)}>
              Security Scan{" "}
              {report.blocked
                ? "— Deployment Blocked"
                : report.is_clean
                  ? "— Repository Clean"
                  : "— Warnings Found"}
            </h3>
            <p className="text-[11px] text-slate-500 dark:text-slate-400 font-medium mt-0.5">
              {report.scanned_files} files scanned · {report.scan_duration_ms}ms
            </p>
          </div>
        </div>

        {/* Severity pills + toggle */}
        <div className="flex items-center gap-2 flex-shrink-0">
          {counts.CRITICAL > 0 && (
            <Badge
              variant="outline"
              className="text-[10px] font-black uppercase bg-red-100 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800/50"
            >
              {counts.CRITICAL} Critical
            </Badge>
          )}
          {counts.HIGH > 0 && (
            <Badge
              variant="outline"
              className="text-[10px] font-black uppercase bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-900/30 dark:text-orange-400 dark:border-orange-800/50 hidden sm:inline-flex"
            >
              {counts.HIGH} High
            </Badge>
          )}
          <span className="text-slate-400 dark:text-slate-600">
            {expanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </span>
        </div>
      </div>

      {/* ── Body ── */}
      {expanded && (
        <div className="p-4 bg-white dark:bg-slate-900/60 space-y-4">
          {/* Summary bar */}
          <div className="flex flex-wrap items-center gap-3">
            {/* Stat pills */}
            {(["CRITICAL", "HIGH", "MEDIUM", "LOW"] as const).map((sev) => {
              const c = counts[sev] ?? 0;
              if (c === 0) return null;
              const cfg = SEVERITY_CONFIG[sev];
              return (
                <div
                  key={sev}
                  className="flex items-center gap-1.5 px-2.5 py-1 rounded-full border text-[10px] font-black uppercase tracking-wider"
                  style={{}}
                >
                  <span className={cn("w-2 h-2 rounded-full", cfg.dot)} />
                  <span className="text-slate-600 dark:text-slate-300">
                    {c} {cfg.label}
                  </span>
                </div>
              );
            })}

            <span className="text-[11px] text-slate-400 dark:text-slate-500 ml-auto font-medium">
              {totalFindings === 0
                ? "No issues found"
                : `${totalFindings} issue${totalFindings !== 1 ? "s" : ""} detected`}
            </span>
          </div>

          {/* Clean state */}
          {report.is_clean && (
            <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800/40">
              <ShieldCheck className="w-5 h-5 text-emerald-500 flex-shrink-0" />
              <div>
                <p className="text-sm font-bold text-emerald-700 dark:text-emerald-400">
                  No secrets or vulnerabilities detected
                </p>
                <p className="text-[11px] text-emerald-600/80 dark:text-emerald-500/70 mt-0.5">
                  This repository is clean and safe to deploy.
                </p>
              </div>
            </div>
          )}

          {/* Blocked banner */}
          {report.blocked && (
            <div className="flex items-start gap-3 px-4 py-3 rounded-xl bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/40">
              <ShieldX className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-extrabold text-red-700 dark:text-red-400">
                  Deployment blocked — CRITICAL secrets found
                </p>
                <p className="text-[11px] text-red-600/80 dark:text-red-500/70 mt-1 leading-relaxed">
                  One or more critical secrets were detected. Remove them from
                  the repository, rotate the leaked credentials, and re-analyze
                  before deploying.
                </p>
              </div>
            </div>
          )}

          {/* Findings list */}
          {report.findings && report.findings.length > 0 && (
            <div className="space-y-2">
              <p className="text-[10px] font-black uppercase tracking-widest text-slate-400 dark:text-slate-500">
                Findings ({totalFindings})
              </p>
              {report.findings.map((finding, i) => (
                <FindingRow key={`${finding.file_path}-${finding.line_number}-${i}`} finding={finding} />
              ))}
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
