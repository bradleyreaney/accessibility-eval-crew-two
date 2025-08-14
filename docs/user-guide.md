# User Guide

Complete guide for accessibility professionals using the evaluation system.

## 🎯 For Accessibility Professionals

This system helps you evaluate and compare accessibility remediation plans using AI-powered analysis with WCAG 2.1 AA alignment.

## 🚀 Getting Started

### What You Need
- **Accessibility audit report** (PDF format)
- **Remediation plans to compare** (PDF format, up to 10 plans)
- **Web browser** (Chrome, Firefox, Safari, or Edge)
- **Internet connection** (for AI analysis)

### 5-Minute Setup
1. **Download the system** from the repository
2. **Install Python 3.11+** if not already installed
3. **Get AI API keys** (Gemini Pro and GPT-4 - see setup guide)
4. **Launch the application** with `streamlit run app/main.py`
5. **Open your browser** to `http://localhost:8501`

## 🌐 Using the Web Interface

### Dashboard Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    📊 Evaluation Dashboard                  │
├─────────────────┬───────────────────────────────────────────┤
│   File Upload   │           Results Display                 │
│                 │                                           │
│ • Audit Report  │  ┌─────────────────────────────────────┐  │
│ • Plan A        │  │         Ranking Results             │  │
│ • Plan B        │  │  1. Plan C (8.7/10) 🏆            │  │
│ • Plan C        │  │  2. Plan A (7.9/10) 🥈            │  │
│ • ...           │  │  3. Plan B (6.5/10) 🥉            │  │
│                 │  └─────────────────────────────────────┘  │
│ [Start Analysis]│                                           │
├─────────────────┼───────────────────────────────────────────┤
│   Progress      │          Visualizations                   │
│                 │                                           │
│ ████████░░ 80%  │  📈 Radar Chart  📊 Bar Chart           │
│ Evaluating...   │  📉 Scatter Plot  🔄 Comparison         │
└─────────────────┴───────────────────────────────────────────┘
```

### Step 1: Upload Your Files

#### Audit Report Upload
1. **Click "Upload Audit Report"** in the sidebar
2. **Select your PDF file** (accessibility audit report)
3. **Wait for processing** - you'll see the document title and page count
4. **Verify content** - check that key findings are visible in the preview

#### Remediation Plans Upload
1. **Click "Upload Remediation Plans"** 
2. **Select multiple PDF files** (hold Ctrl/Cmd for multiple selection)
3. **Review plan list** - each plan will show title and page count
4. **Add more plans** if needed (up to 10 total)

#### Supported File Types
- **PDF only** - other formats not currently supported
- **Maximum size**: 50MB per file
- **Text-based PDFs** work best (scanned PDFs may have issues)

### Step 2: Start the Evaluation

#### Launch Analysis
1. **Click "Start Evaluation"** button
2. **Monitor progress** in the sidebar progress bar
3. **View real-time status** updates:
   - "Parsing documents..." 
   - "Initializing AI agents..."
   - "Primary judge evaluating Plan A..."
   - "Secondary judge evaluating Plan A..."
   - "Calculating consensus scores..."
   - "Generating final analysis..."

#### Processing Time
- **Single plan**: ~2-3 minutes
- **Multiple plans**: ~5-10 minutes
- **Complex plans**: Up to 15 minutes

### Step 3: Review Results

#### Rankings Dashboard
```
🏆 Final Rankings
┌──────────┬───────────────┬─────────┬──────────────────────┐
│   Rank   │   Plan Name   │  Score  │    Key Strengths     │
├──────────┼───────────────┼─────────┼──────────────────────┤
│    1     │   Plan C      │  8.7    │ Strategic focus,     │
│          │               │         │ detailed technical   │
├──────────┼───────────────┼─────────┼──────────────────────┤
│    2     │   Plan A      │  7.9    │ Comprehensive,       │
│          │               │         │ good long-term       │
├──────────┼───────────────┼─────────┼──────────────────────┤
│    3     │   Plan B      │  6.5    │ Adequate coverage,   │
│          │               │         │ needs refinement     │
└──────────┴───────────────┴─────────┴──────────────────────┘
```

#### Detailed Score Breakdown
For each plan, you'll see scores across four criteria:

**🎯 Strategic Prioritization (40%)**
- How well the plan focuses on high-impact accessibility issues
- Example: "Prioritizes critical keyboard navigation issues affecting all users"

**🔧 Technical Specificity (30%)**  
- Quality of implementation guidance and technical detail
- Example: "Provides specific ARIA label examples and code snippets"

**📋 Comprehensiveness (20%)**
- Coverage of all identified accessibility barriers
- Example: "Addresses 18 of 20 audit findings with clear solutions"

**🚀 Long-term Vision (10%)**
- Sustainability and ongoing accessibility planning
- Example: "Includes staff training and automated testing integration"

#### Interactive Visualizations

**📊 Radar Chart**: Compare plans across all four criteria
```
        Strategic (8.5)
             ╱│╲
      (7.2) ╱ │ ╲ (8.0)
   Technical│ │ │Long-term
           ╱   │   ╲
          ╱    │    ╲
    (6.8) ──────────── 
      Comprehensive
```

**📈 Scatter Plot**: View score distribution and identify outliers
**📊 Bar Chart**: Direct comparison of overall scores

### Step 4: Download Reports

#### Available Report Formats

**📄 PDF Reports** (4 types available):
- **Executive Summary**: 2-page overview for leadership
- **Detailed Report**: Complete analysis with full reasoning
- **Comparative Analysis**: Side-by-side plan comparison
- **Summary Report**: Quick reference with key findings

**📊 Data Exports**:
- **CSV**: Spreadsheet-compatible scores and rankings
- **JSON**: Complete data for further analysis

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
