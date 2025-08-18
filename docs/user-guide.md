// ...existing code...
# User Guide

Complete guide for accessibility professionals using the evaluation system.

## 🎯 For Accessibility Professionals

This system helps you evaluate and compare accessibility remediation plans using AI-powered analysis with WCAG 2.1 AA alignment.

## 🚀 Getting Started

### What You Need
### What You Need
- **Accessibility audit report** (PDF format)
- **Remediation plans to compare** (PDF format, up to 10 plans)
- **Internet connection** (for AI analysis)
- **API Keys** (Gemini Pro and GPT-4 - required as environment variables)

### 5-Minute Setup
1. **Download the system** from the repository
2. **Install Python 3.11+** if not already installed
3. **Get AI API keys** (Gemini Pro and GPT-4 - see setup guide below)
4. **Configure environment variables** (REQUIRED - see Configuration section below)
5. **Run the CLI** with `python main.py --audit-dir data/audit-reports --plans-dir data/remediation-plans [other options]`
6. **Review generated reports** in `output/reports/`

### � Required Configuration

**Environment Variables Required**: This application uses environment-only configuration for enhanced security. Both API keys must be set as environment variables before starting the application.

#### For Local Development:
1. Copy `.env.example` to `.env` in the project root
2. Edit the `.env` file with your API keys:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```
3. Restart the application

#### For Production/Server Deployment:
Set environment variables in your deployment platform:
- `GOOGLE_API_KEY=your_gemini_api_key`
- `OPENAI_API_KEY=your_openai_api_key`

**⚠️ Important**: The CLI will not run without both environment variables properly configured. You can set them in your `.env` file or export them in your shell.


## �️ Using the Command-Line Interface (CLI)

All user interaction is now via the CLI. The previous browser-based workflows and Docker/container deployment are deprecated and no longer supported.

### Step 1: Prepare Your Files

- Place your audit report PDF(s) in `data/audit-reports/`
- Place your remediation plan PDF(s) in `data/remediation-plans/`

### Step 2: Run the Evaluation

Use the CLI to start the analysis:
```bash
python main.py --audit-dir data/audit-reports --plans-dir data/remediation-plans [other options]
```

#### Common options:
- `--output output/reports/` (set output directory)
- `--mode single|parallel|sequential` (choose evaluation mode)
- `--timeout 30` (set timeout in seconds)
- `--verbose` (show detailed logs)

### Step 3: Review Results

After completion, reports will be generated in the output directory:
- **PDF Reports**: Executive Summary, Detailed Report, Comparative Analysis, Summary Report
- **CSV/JSON Exports**: For further analysis

### Step 4: Interpreting Results

Open the generated PDF, CSV, or JSON files to review rankings, scores, and detailed breakdowns for each plan. All scoring criteria and methodology remain unchanged from the previous UI.

### CLI Tips
- Ensure your environment variables are set before running the CLI
- Use text-based PDFs for best results
- Review logs for troubleshooting information
#### Using the Reports

**For Leadership Presentations**:
- Use Executive Summary PDF
- Include ranking visualization screenshots
- Focus on top recommendation and business impact

**For Implementation Teams**:
- Use Detailed Report PDF
- Review technical specificity sections
- Follow implementation recommendations

**For Further Analysis**:
- Export CSV for custom charts and analysis
- Use JSON data for integration with other tools

## 🎯 Understanding the AI Analysis

### Dual-Judge System
The system uses two AI judges for reliability:

**🤖 Primary Judge (Gemini Pro)**:
- Provides initial detailed evaluation
- Focuses on accessibility expertise
- Generates comprehensive reasoning

**🤖 Secondary Judge (GPT-4)**:
- Provides independent assessment
- Cross-validates primary evaluation
- Identifies potential biases or oversights

**🔄 Consensus Engine**:
- Automatically resolves minor scoring differences
- Escalates major disagreements for review
- Ensures consistent, reliable results

### 🛡️ LLM Error Resilience

The system includes robust error handling that ensures your evaluation continues even if one AI service becomes temporarily unavailable:

**Graceful Degradation**:
- If one LLM fails, the system automatically uses the other
- Partial results are provided instead of complete failure
- Failed evaluations are clearly marked as "NA" in reports
- System continues operating with reduced capability

**What You'll See**:
- **Normal Operation**: Both LLMs available, full evaluation capability
- **Partial Operation**: One LLM available, some evaluations may be marked "NA"
- **Status Reporting**: Clear indication of LLM availability in CLI output
- **Transparent Results**: Failed evaluations clearly identified in reports

**Example Output**:
```
✅ LLM availability check complete:
   Gemini Pro: Available
   GPT-4: Unavailable (Rate limit exceeded)
⚠️  Operating with 1 available LLM(s)
📊 Partial evaluation completed: 8/10 plans evaluated (80.0%)
```

### Evaluation Methodology

#### WCAG 2.1 AA Alignment
All evaluations are based on Web Content Accessibility Guidelines:
- **Level A**: Critical barriers (highest priority)
- **Level AA**: Standard requirements (primary focus)
- **Level AAA**: Enhanced features (considered but lower priority)

#### Evidence-Based Scoring
Each score includes detailed reasoning:
- **Specific examples** from the remediation plan
- **WCAG guideline references** where applicable
- **Implementation feasibility** assessment
- **User impact** analysis

## 🔧 Practical Tips

### Preparing Your Files

**Audit Report Best Practices**:
- ✅ Include executive summary with severity breakdown
- ✅ Provide specific WCAG violation details
- ✅ Include user impact descriptions
- ✅ List priority recommendations

**Remediation Plan Best Practices**:
- ✅ Clear implementation steps and timelines
- ✅ Specific technical solutions and code examples
- ✅ Resource requirements and cost estimates
- ✅ Success metrics and testing procedures

### Optimizing Results

**For Higher Scores**:
- Focus on high-impact, critical accessibility issues first
- Provide specific, actionable implementation guidance
- Address comprehensive coverage of audit findings
- Include long-term sustainability planning

**For Faster Processing**:
- Use text-based PDFs (not scanned images)
- Keep file sizes reasonable (<10MB when possible)
- Ensure clear document structure and headings

### Common Issues & Solutions

**"No text extracted from PDF"**:
- ❌ File is image-based or scanned
- ✅ Solution: Convert to text-based PDF or use OCR

**"Evaluation timeout"**:
- ❌ Plan is extremely long or complex
- ✅ Solution: Break into smaller sections or simplify

**"LLM connection error"**:
- ❌ API keys not configured or invalid
- ✅ Solution: Check .env file and API key validity

## 📊 Interpreting Results

### Score Ranges Guide
- **9.0-10.0**: 🏆 **Excellent** - Implement immediately
- **8.0-8.9**: 🥈 **Very Good** - Minor tweaks needed
- **7.0-7.9**: 🥉 **Good** - Some improvements required
- **6.0-6.9**: ✅ **Adequate** - Moderate revisions needed
- **5.0-5.9**: ⚠️ **Below Standard** - Significant work required
- **< 5.0**: ❌ **Poor** - Major revision needed

### Making Implementation Decisions

**Choose the top-ranked plan when**:
- Score difference is >1.0 point from next option
- Strategic prioritization score is strong (>8.0)
- Technical specificity meets your team's capabilities

**Consider hybrid approaches when**:
- Multiple plans score within 0.5 points
- Different plans excel in different criteria
- You have capacity to combine best elements

**Request plan revisions when**:
- All plans score below 7.0
- Critical gaps identified in comprehensiveness
- Long-term vision planning is insufficient

## 🔗 Getting Help

### Built-in Support
- **Hover tooltips**: Explanations for all scores and criteria
- **Progress indicators**: Real-time status updates
- **Error messages**: Clear guidance when issues occur

### Documentation Resources
- **[API Reference](../api-reference/)**: Technical implementation details
- **[Examples](../examples/)**: Code examples and usage patterns
- **[Troubleshooting](../troubleshooting/)**: Common issues and solutions

### Support Channels
- **GitHub Issues**: Report bugs or request features
- **Documentation**: Comprehensive guides and references
- **Community**: Share experiences and best practices

---

**Ready to make data-driven accessibility improvement decisions!** 🎯
