# User Guide

Complete guide for accessibility professionals using the evaluation system with LLM error resilience support.

## 🎯 For Accessibility Professionals

This system helps you evaluate and compare accessibility remediation plans using AI-powered analysis with WCAG 2.1 AA alignment. The system includes robust error handling that ensures you get partial results even when one AI service is temporarily unavailable.

## 🚀 Getting Started

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

### 🔒 Required Configuration

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

## 🛡️ LLM Error Resilience

The system includes robust error handling that ensures you get results even when one AI service is temporarily unavailable:

### How It Works
- **Automatic Fallback**: If one AI service fails, the system automatically uses the other
- **Partial Results**: You get evaluations for available plans, with unavailable ones marked as "NA"
- **Clear Reporting**: Reports clearly indicate which evaluations couldn't be completed and why
- **No Data Loss**: Successful evaluations are preserved and reported normally

### Understanding NA Sections
When you see "NA" (Not Available) in your reports, it means:
- The evaluation couldn't be completed due to AI service unavailability
- The system tried both AI services but both were unavailable for that specific plan
- The report includes the reason (e.g., "Rate limit exceeded", "Connection timeout")

### Example Output
```
✅ LLM availability check complete:
   Gemini Pro: Available
   GPT-4: Unavailable (Rate limit exceeded)
⚠️  Operating with 1 available LLM(s)
📊 Partial evaluation completed: 8/10 plans evaluated (80.0%)
```

## 💻 Using the Command-Line Interface (CLI)

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
- `--verbose` (show detailed logs including LLM status)

### Step 3: Review Results

After completion, reports will be generated in the output directory:
- **PDF Reports**: Executive Summary, Detailed Report, Comparative Analysis, Summary Report
- **CSV/JSON Exports**: For further analysis
- **Completion Summary**: Shows evaluation completion statistics and LLM availability

### Step 4: Interpreting Results

Open the generated PDF, CSV, or JSON files to review rankings, scores, and detailed breakdowns for each plan. All scoring criteria and methodology remain unchanged from the previous UI.

#### Understanding Partial Results
If you see partial results with some plans marked as "NA":

1. **Check the Completion Summary**: Look at the completion percentage and available LLMs
2. **Review NA Reasons**: Each NA section explains why the evaluation couldn't be completed
3. **Focus on Available Results**: Use the completed evaluations for your decision-making
4. **Consider Retrying**: You can re-run the evaluation later when services are available

### CLI Tips
- Ensure your environment variables are set before running the CLI
- Use text-based PDFs for best results
- Review logs for troubleshooting information
- Use `--verbose` to see detailed LLM status information

## 📊 Using the Reports

**For Leadership Presentations**:
- Use Executive Summary PDF
- Include ranking visualization screenshots
- Focus on top recommendation and business impact
- Note any partial completion status

**For Implementation Teams**:
- Use Detailed Report PDF
- Review technical specificity sections
- Follow implementation recommendations
- Check for any NA sections that need follow-up

**For Further Analysis**:
- Export CSV for custom charts and analysis
- Use JSON data for integration with other tools
- Review completion statistics for system health

## 🎯 Understanding the AI Analysis

### Evaluation Criteria
The system evaluates plans using four weighted criteria:

- **Strategic Prioritization (40%)**: How well the plan addresses high-impact accessibility issues
- **Technical Specificity (30%)**: Level of detail in implementation guidance
- **Comprehensiveness (20%)**: Coverage of audit findings and WCAG guidelines
- **Long-term Vision (10%)**: Sustainability and future-proofing considerations

### WCAG Alignment
Evaluations are aligned with WCAG 2.1 AA standards:
- **Level A**: Basic accessibility requirements (must be addressed)
- **Level AA**: Enhanced accessibility features (recommended priority)
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

**"Some evaluations marked as NA"**:
- ❌ One or both AI services temporarily unavailable
- ✅ Solution: Check completion summary for details, retry later if needed

## 📊 Interpreting Results

### Score Ranges Guide
- **9.0-10.0**: 🏆 **Excellent** - Implement immediately
- **8.0-8.9**: 🥈 **Very Good** - Minor tweaks needed
- **7.0-7.9**: 🥉 **Good** - Some improvements required
- **6.0-6.9**: ✅ **Adequate** - Moderate revisions needed
- **5.0-5.9**: ⚠️ **Below Standard** - Significant work required
- **< 5.0**: ❌ **Poor** - Major revision needed
- **NA**: 🔄 **Not Available** - Evaluation could not be completed

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

**Handle partial results when**:
- Some plans are marked as "NA"
- Focus on completed evaluations for decision-making
- Consider retrying failed evaluations later
- Use completion statistics to understand system health

## 🔗 Getting Help

### Built-in Support
- **Hover tooltips**: Explanations for all scores and criteria
- **Progress indicators**: Real-time status updates
- **Error messages**: Clear guidance when issues occur
- **Completion summaries**: Detailed statistics on evaluation success

### Documentation Resources
- **[API Reference](../api-reference/)**: Technical implementation details
- **[Examples](../examples/)**: Code examples and usage patterns
- **[Troubleshooting](../troubleshooting/)**: Common issues and solutions
- **[LLM Error Resilience](../features/llm-error-resilience.md)**: Detailed resilience feature documentation

### Support Channels
- **GitHub Issues**: Report bugs or request features
- **Documentation**: Comprehensive guides and references
- **Community**: Share experiences and best practices

---

**Ready to make data-driven accessibility improvement decisions!** 🎯
