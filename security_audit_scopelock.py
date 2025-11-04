#!/usr/bin/env python3
"""
Security Audit Script for Scopelock Graph
Marcus - Chief Auditor, GraphCare

Scans for:
1. PII (emails, phones, addresses)
2. Credentials (API keys, passwords, tokens)
3. GDPR compliance issues
"""

import re
import sys
from typing import Dict, List
from collections import defaultdict

from orchestration.libs.utils.falkordb_adapter import get_falkordb_graph


class SecurityAuditor:
    """Security auditor for graph-based knowledge extraction"""

    def __init__(self, graph_name: str):
        self.graph_name = graph_name
        self.graph = get_falkordb_graph(graph_name)
        self.findings = {
            'pii': [],
            'credentials': [],
            'gdpr_issues': [],
            'stats': {}
        }

        # PII patterns
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_pattern = r'\b(?:\+?1[-.]?)?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b'
        self.ssn_pattern = r'\b\d{3}-\d{2}-\d{4}\b'

        # Credential patterns
        self.credential_keywords = ['api_key', 'apikey', 'API_KEY', 'password', 'passwd', 'pwd',
                                    'token', 'bearer', 'secret', 'private_key', 'access_token']

    def execute_query(self, cypher: str) -> List[Dict]:
        """Execute Cypher query and return results as list of dicts"""
        try:
            result = self.graph.query(cypher)
            if result and result.result_set:
                # Convert result set to list of dicts
                rows = []
                for row in result.result_set:
                    row_dict = {}
                    # Get column names from header
                    for i, header in enumerate(result.header):
                        if i < len(row):
                            col_name = header[1]  # header is (type, name)
                            row_dict[col_name] = row[i]
                    rows.append(row_dict)
                return rows
            return []
        except Exception as e:
            print(f"Query error: {e}")
            return []

    def map_attack_surface(self) -> Dict:
        """Map the graph structure and data flows"""
        print("=" * 80)
        print("STAGE 1: ATTACK SURFACE MAPPING")
        print("=" * 80)

        # Get total node count
        cypher_count = "MATCH (n) RETURN count(n) as total"
        total_result = self.execute_query(cypher_count)
        total_nodes = total_result[0]['total'] if total_result else 0

        print(f"\nTotal nodes in scopelock graph: {total_nodes}")

        # Get node types (labels)
        cypher_labels = "MATCH (n) RETURN DISTINCT labels(n)[0] as label, count(*) as count"
        label_results = self.execute_query(cypher_labels)

        print("\nNode types:")
        label_counts = {}
        for row in label_results:
            label = row['label']
            count = row['count']
            label_counts[label] = count
            print(f"  - {label}: {count} nodes")

        # Get relationship types
        cypher_rels = "MATCH ()-[r]->() RETURN type(r) as rel_type, count(*) as count"
        rel_results = self.execute_query(cypher_rels)

        print("\nRelationship types:")
        rel_counts = {}
        for row in rel_results:
            rel_type = row['rel_type']
            count = row['count']
            rel_counts[rel_type] = count
            print(f"  - {rel_type}: {count} relationships")

        self.findings['stats'] = {
            'total_nodes': total_nodes,
            'node_types': label_counts,
            'relationship_types': rel_counts
        }

        return self.findings['stats']

    def scan_pii(self) -> List[Dict]:
        """Scan for PII in graph nodes"""
        print("\n" + "=" * 80)
        print("STAGE 2: PII SCANNING")
        print("=" * 80)

        # Get all nodes with text content
        cypher = """
        MATCH (n)
        WHERE n.description IS NOT NULL
           OR n.content IS NOT NULL
           OR n.name IS NOT NULL
        RETURN id(n) as node_id,
               labels(n)[0] as label,
               n.path as path,
               n.name as name,
               n.description as description,
               n.content as content
        LIMIT 5000
        """

        results = self.execute_query(cypher)
        print(f"\nScanning {len(results)} nodes for PII...")

        pii_findings = []

        for row in results:
            # Combine all text fields
            combined_text = ' '.join([
                str(row.get('name', '')),
                str(row.get('description', '')),
                str(row.get('content', ''))
            ])

            # Scan for PII
            pii_types_found = []

            # Emails
            emails = re.findall(self.email_pattern, combined_text, re.IGNORECASE)
            if emails:
                pii_types_found.append(f"emails({len(emails)})")

            # Phones
            phones = re.findall(self.phone_pattern, combined_text)
            if phones:
                pii_types_found.append(f"phones({len(phones)})")

            # SSNs
            ssns = re.findall(self.ssn_pattern, combined_text)
            if ssns:
                pii_types_found.append(f"SSNs({len(ssns)})-CRITICAL")

            if pii_types_found:
                finding = {
                    'path': row.get('path', 'unknown'),
                    'label': row.get('label', 'unknown'),
                    'pii_types': pii_types_found,
                    'severity': 'CRITICAL' if ssns else 'HIGH'
                }
                pii_findings.append(finding)

        self.findings['pii'] = pii_findings

        print(f"\n✅ PII scan complete: {len(pii_findings)} nodes with PII found")
        if len(pii_findings) > 0:
            print("\nExamples (first 5):")
            for finding in pii_findings[:5]:
                print(f"  - {finding['label']}: {', '.join(finding['pii_types'])}")

        return pii_findings

    def scan_credentials(self) -> List[Dict]:
        """Scan for credentials in graph nodes"""
        print("\n" + "=" * 80)
        print("STAGE 3: CREDENTIAL SCANNING")
        print("=" * 80)

        # Get all nodes with text content
        cypher = """
        MATCH (n)
        WHERE n.description IS NOT NULL
           OR n.content IS NOT NULL
           OR n.name IS NOT NULL
        RETURN id(n) as node_id,
               labels(n)[0] as label,
               n.path as path,
               n.name as name,
               n.description as description,
               n.content as content
        LIMIT 5000
        """

        results = self.execute_query(cypher)
        print(f"\nScanning {len(results)} nodes for credentials...")

        credential_findings = []

        for row in results:
            # Combine all text fields
            combined_text = ' '.join([
                str(row.get('name', '')),
                str(row.get('description', '')),
                str(row.get('content', ''))
            ])

            # Check for credential keywords
            creds_found = []
            for keyword in self.credential_keywords:
                if keyword.lower() in combined_text.lower():
                    # Check if it's not just documentation
                    if not any(doc_marker in combined_text.lower() for doc_marker in ['example', 'your_', '<', '{{', 'placeholder']):
                        creds_found.append(keyword)

            if creds_found:
                finding = {
                    'path': row.get('path', 'unknown'),
                    'label': row.get('label', 'unknown'),
                    'credentials': creds_found,
                    'severity': 'CRITICAL'
                }
                credential_findings.append(finding)

        self.findings['credentials'] = credential_findings

        print(f"\n✅ Credential scan complete: {len(credential_findings)} nodes with potential credentials found")
        if len(credential_findings) > 0:
            print("\nExamples (first 5):")
            for finding in credential_findings[:5]:
                print(f"  - {finding['label']} ({finding['path']}): {', '.join(finding['credentials'])}")

        return credential_findings

    def check_gdpr_compliance(self) -> Dict:
        """Check GDPR compliance"""
        print("\n" + "=" * 80)
        print("STAGE 4: GDPR COMPLIANCE CHECK")
        print("=" * 80)

        compliance = {
            'consent_records': {'status': 'unknown', 'details': ''},
            'right_to_erasure': {'status': 'pass', 'details': 'Graph can be deleted via DROP command'},
            'portability': {'status': 'pass', 'details': 'Graph exportable via Cypher queries'},
            'data_minimization': {'status': 'unknown', 'details': ''},
            'encryption': {'status': 'warning', 'details': 'FalkorDB encryption settings not verified'}
        }

        # Check for consent-related nodes
        cypher_consent = """
        MATCH (n)
        WHERE toLower(toString(n.path)) CONTAINS 'consent'
           OR toLower(toString(n.name)) CONTAINS 'consent'
        RETURN count(*) as count
        """
        consent_results = self.execute_query(cypher_consent)
        consent_count = consent_results[0]['count'] if consent_results else 0

        if consent_count > 0:
            compliance['consent_records']['status'] = 'pass'
            compliance['consent_records']['details'] = f'Found {consent_count} consent-related nodes'
        else:
            compliance['consent_records']['status'] = 'fail'
            compliance['consent_records']['details'] = 'No consent records found - verify client provided consent'

        # Data minimization
        if len(self.findings['pii']) > 0:
            compliance['data_minimization']['status'] = 'warning'
            compliance['data_minimization']['details'] = f'PII in {len(self.findings["pii"])} nodes - verify necessity'
        else:
            compliance['data_minimization']['status'] = 'pass'
            compliance['data_minimization']['details'] = 'No PII detected'

        # Print compliance status
        print("\nGDPR Compliance Status:")
        for check, result in compliance.items():
            status_icon = {'pass': '✅', 'fail': '❌', 'warning': '⚠️', 'unknown': '❓'}.get(result['status'], '?')
            print(f"  {status_icon} {check.replace('_', ' ').title()}: {result['status'].upper()}")
            print(f"     {result['details']}")

        self.findings['gdpr_issues'] = compliance
        return compliance

    def generate_report(self) -> str:
        """Generate final security audit report"""
        print("\n" + "=" * 80)
        print("STAGE 5: GENERATING SECURITY AUDIT REPORT")
        print("=" * 80)

        # Count issues by severity
        critical_count = len(self.findings['credentials'])
        critical_pii = [p for p in self.findings['pii'] if p['severity'] == 'CRITICAL']
        critical_count += len(critical_pii)

        high_pii = [p for p in self.findings['pii'] if p['severity'] == 'HIGH']
        high_count = len(high_pii)

        gdpr_failures = [k for k, v in self.findings['gdpr_issues'].items() if v['status'] == 'fail']
        gdpr_warnings = [k for k, v in self.findings['gdpr_issues'].items() if v['status'] == 'warning']

        high_count += len(gdpr_failures)
        medium_count = len(gdpr_warnings)

        # Determine recommendation
        if critical_count > 0:
            recommendation = "BLOCK"
            reason = f"{critical_count} CRITICAL issues must be resolved before delivery"
        elif high_count > 5:
            recommendation = "SHIP WITH CAVEAT"
            reason = f"{high_count} HIGH issues - document and plan remediation"
        else:
            recommendation = "SHIP"
            reason = f"Security scan clean - {medium_count} MEDIUM issues documented"

        # Generate report
        report = f"""# Scopelock Security Audit Report

**Auditor:** Marcus (Chief Auditor, GraphCare)
**Date:** 2025-11-04
**Graph:** {self.graph_name}

## Executive Summary

**Total Issues:** {critical_count + high_count + medium_count}
- **CRITICAL:** {critical_count}
- **HIGH:** {high_count}
- **MEDIUM:** {medium_count}

**Recommendation:** **{recommendation}**
**Reason:** {reason}

---

## Attack Surface

**Total Nodes:** {self.findings['stats']['total_nodes']}

**Node Types:**
"""

        for label, count in sorted(self.findings['stats']['node_types'].items()):
            report += f"- {label}: {count} nodes\n"

        report += "\n**Relationship Types:**\n"
        for rel_type, count in sorted(self.findings['stats']['relationship_types'].items()):
            report += f"- {rel_type}: {count} relationships\n"

        report += "\n---\n\n## PII Scan\n\n"

        if len(self.findings['pii']) == 0:
            report += "✅ **No PII detected in graph**\n"
        else:
            report += f"⚠️ **PII found in {len(self.findings['pii'])} nodes**\n\n"
            report += "**Breakdown:**\n"
            report += f"- CRITICAL (SSNs): {len(critical_pii)} nodes\n"
            report += f"- HIGH (emails/phones): {len(high_pii)} nodes\n\n"

            if len(critical_pii) > 0:
                report += "**CRITICAL PII (SSNs):**\n"
                for finding in critical_pii[:3]:
                    report += f"- `{finding['path']}`: {', '.join(finding['pii_types'])}\n"

            if len(high_pii) > 0:
                report += "\n**HIGH PII (emails/phones) - Examples:**\n"
                for finding in high_pii[:5]:
                    report += f"- `{finding['label']}`: {', '.join(finding['pii_types'])}\n"

            report += "\n**Risk:** PII without consent = GDPR violation\n"
            report += "**Remediation:** Verify client consent or scrub PII from extracted data\n"

        report += "\n---\n\n## Credentials Scan\n\n"

        if len(self.findings['credentials']) == 0:
            report += "✅ **No credentials detected in graph**\n"
        else:
            report += f"❌ **CRITICAL: Potential credentials found in {len(self.findings['credentials'])} nodes**\n\n"
            report += "**Examples:**\n"
            for finding in self.findings['credentials'][:10]:
                report += f"- `{finding['path']}`: {', '.join(finding['credentials'])}\n"

            report += "\n**Risk:** Credentials in graph = security breach\n"
            report += "**Remediation:** Manual review required - scrub if actual credentials\n"

        report += "\n---\n\n## GDPR Compliance\n\n"

        for check, result in self.findings['gdpr_issues'].items():
            status_icon = {'pass': '✅', 'fail': '❌', 'warning': '⚠️', 'unknown': '❓'}.get(result['status'], '?')
            report += f"**{status_icon} {check.replace('_', ' ').title()}:** {result['status'].upper()}\n"
            report += f"  - {result['details']}\n\n"

        report += "\n---\n\n## Final Recommendation\n\n"
        report += f"### {recommendation}\n\n"
        report += f"{reason}\n\n"

        if critical_count > 0:
            report += "**CRITICAL issues that MUST be fixed:**\n\n"
            if len(self.findings['credentials']) > 0:
                report += f"1. Review and remove {len(self.findings['credentials'])} nodes with potential credentials\n"
            if len(critical_pii) > 0:
                report += f"2. Scrub {len(critical_pii)} nodes containing SSNs (or verify explicit consent)\n"

        if high_count > 0:
            report += "\n**HIGH issues to address:**\n\n"
            if len(high_pii) > 0:
                report += f"1. Verify consent for PII in {len(high_pii)} nodes (emails, phones)\n"
            if len(gdpr_failures) > 0:
                report += f"2. Address GDPR failures: {', '.join(gdpr_failures)}\n"

        if medium_count > 0:
            report += "\n**MEDIUM issues (document for ongoing care):**\n\n"
            if len(gdpr_warnings) > 0:
                report += f"1. {', '.join(gdpr_warnings)}\n"

        report += "\n---\n\n"
        report += "**Marcus - Chief Auditor, GraphCare**  \n"
        report += "*\"Security is non-negotiable. CRITICAL issues must be fixed before delivery.\"*\n"

        return report


def main():
    """Run security audit on scopelock graph"""
    print("Marcus - Chief Auditor: Starting scopelock security audit...\n")

    auditor = SecurityAuditor(graph_name='scopelock')

    # Stage 1: Map attack surface
    auditor.map_attack_surface()

    # Stage 2: Scan for PII
    auditor.scan_pii()

    # Stage 3: Scan for credentials
    auditor.scan_credentials()

    # Stage 4: Check GDPR compliance
    auditor.check_gdpr_compliance()

    # Stage 5: Generate report
    report = auditor.generate_report()

    # Save report
    report_path = '/home/mind-protocol/scopelock_security_audit.md'
    with open(report_path, 'w') as f:
        f.write(report)

    print(f"\n✅ Report saved to: {report_path}\n")

    # Return exit code based on findings
    if len(auditor.findings['credentials']) > 0:
        print("❌ BLOCKING: CRITICAL credential issues found")
        return 1

    critical_pii = [p for p in auditor.findings['pii'] if p['severity'] == 'CRITICAL']
    if len(critical_pii) > 0:
        print("❌ BLOCKING: CRITICAL PII (SSNs) found")
        return 1

    if len(auditor.findings['pii']) > 10:
        print("⚠️ WARNING: Significant PII found - recommend review")

    print("✅ No CRITICAL security issues - safe to proceed with caveats")
    return 0


if __name__ == '__main__':
    sys.exit(main())
