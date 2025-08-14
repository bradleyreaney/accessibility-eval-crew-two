# Evaluation Criteria Reference

Comprehensive reference for the WCAG-aligned evaluation framework used by the LLM judges.

## 🎯 Weighted Evaluation Criteria

### 1. Strategic Prioritization (40% weight)

**Definition**: Focus on high-impact accessibility issues that provide maximum benefit.

**Evaluation Points**:
- ✅ **Issue Severity Assessment**: Prioritizes critical and high-severity accessibility barriers
- ✅ **User Impact Analysis**: Considers impact on users with different disabilities
- ✅ **Implementation Feasibility**: Balances impact with realistic implementation timelines
- ✅ **Resource Allocation**: Efficient use of available resources (time, budget, personnel)
- ✅ **Risk Mitigation**: Addresses compliance risks and legal exposure

**Scoring Guidelines**:
- **9-10**: Excellent prioritization focusing on high-impact, critical issues first
- **7-8**: Good prioritization with minor optimization opportunities
- **5-6**: Adequate prioritization but some low-impact items ranked too highly
- **3-4**: Poor prioritization mixing critical and minor issues
- **1-2**: No clear prioritization strategy evident

**WCAG Alignment**:
- **Level A**: Critical barriers that prevent access entirely
- **Level AA**: Standard accessibility requirements (primary focus)
- **Level AAA**: Enhanced accessibility features (lower priority)

### 2. Technical Specificity (30% weight)

**Definition**: Quality and detail of implementation guidance and technical solutions.

**Evaluation Points**:
- ✅ **Implementation Detail**: Specific, actionable technical instructions
- ✅ **Code Examples**: Concrete examples of accessible implementations
- ✅ **Testing Procedures**: Clear validation and testing methodologies
- ✅ **Tool Recommendations**: Specific accessibility tools and resources
- ✅ **Standards Compliance**: Adherence to WCAG 2.1 AA standards

**Scoring Guidelines**:
- **9-10**: Highly detailed with specific implementation steps and code examples
- **7-8**: Good technical detail with clear implementation guidance
- **5-6**: Adequate technical information but some gaps in specificity
- **3-4**: Vague technical guidance lacking implementation detail
- **1-2**: Generic recommendations without specific technical direction

**Technical Categories**:
- **Semantic HTML**: Proper markup structure and ARIA usage
- **Keyboard Navigation**: Tab order, focus management, keyboard shortcuts
- **Screen Reader Support**: ARIA labels, descriptions, live regions
- **Visual Design**: Color contrast, text sizing, visual indicators
- **Interactive Elements**: Form accessibility, button states, error handling

### 3. Comprehensiveness (20% weight)

**Definition**: Complete coverage of identified accessibility issues without significant gaps.

**Evaluation Points**:
- ✅ **Issue Coverage**: Addresses all major accessibility barriers found in audit
- ✅ **User Journey Mapping**: Considers accessibility across entire user workflows
- ✅ **Multiple Disability Types**: Addresses visual, auditory, motor, and cognitive disabilities
- ✅ **Content Types**: Covers text, images, videos, interactive elements, forms
- ✅ **Platform Considerations**: Web, mobile, assistive technology compatibility

**Scoring Guidelines**:
- **9-10**: Comprehensive coverage of all identified issues and user scenarios
- **7-8**: Good coverage with minor gaps in specific areas
- **5-6**: Adequate coverage but misses some important accessibility aspects
- **3-4**: Limited coverage focusing on only major issues
- **1-2**: Incomplete coverage missing significant accessibility barriers

**Coverage Areas**:
- **Perceivable**: Text alternatives, captions, color/contrast, resizable text
- **Operable**: Keyboard access, timing controls, seizure prevention, navigation
- **Understandable**: Readable text, predictable functionality, input assistance
- **Robust**: Compatible with assistive technologies, valid code

### 4. Long-term Vision (10% weight)

**Definition**: Sustainability, scalability, and strategic planning for ongoing accessibility.

**Evaluation Points**:
- ✅ **Maintenance Planning**: Ongoing accessibility maintenance and monitoring
- ✅ **Team Training**: Staff education and accessibility skill development
- ✅ **Process Integration**: Embedding accessibility into development workflows
- ✅ **Future Scalability**: Plans that scale with organizational growth
- ✅ **Continuous Improvement**: Monitoring, testing, and iterative enhancement

**Scoring Guidelines**:
- **9-10**: Excellent long-term planning with sustainability and scalability
- **7-8**: Good forward-thinking with solid maintenance planning
- **5-6**: Adequate future planning but limited long-term considerations
- **3-4**: Minimal long-term planning focusing mainly on immediate fixes
- **1-2**: No evidence of long-term accessibility strategy

**Long-term Elements**:
- **Training Programs**: Regular accessibility training for development teams
- **Automated Testing**: Integration of accessibility testing in CI/CD pipelines
- **User Feedback**: Channels for ongoing accessibility feedback from users
- **Compliance Monitoring**: Regular audits and accessibility health checks
- **Accessibility Culture**: Building organization-wide accessibility awareness

## 🏆 Overall Scoring Methodology

### Weighted Score Calculation
```python
weighted_score = (
    (strategic_prioritization * 0.40) +
    (technical_specificity * 0.30) +
    (comprehensiveness * 0.20) +
    (long_term_vision * 0.10)
)
```

### Score Interpretation
- **9.0-10.0**: 🏆 **Excellent** - Ready for immediate implementation
- **8.0-8.9**: 🥈 **Very Good** - Minor refinements recommended
- **7.0-7.9**: 🥉 **Good** - Some improvements needed
- **6.0-6.9**: ✅ **Adequate** - Moderate revisions required
- **5.0-5.9**: ⚠️ **Below Standard** - Significant improvements needed
- **< 5.0**: ❌ **Poor** - Major revision or replacement recommended

## 📊 Judge Consensus Guidelines

### Agreement Thresholds
- **Minor Disagreement**: <2 points difference → Automated averaging
- **Moderate Disagreement**: 2-3 points difference → Evidence quality assessment
- **Major Disagreement**: >3 points difference → Human escalation required

### Conflict Resolution Process
1. **Automatic Resolution**: Simple averaging for minor differences
2. **Evidence Assessment**: Detailed rationale analysis for moderate conflicts
3. **Human Review**: Expert review for major disagreements
4. **Final Determination**: Documented decision with reasoning

## 🎯 WCAG 2.1 AA Compliance Mapping

### Principle 1: Perceivable
- **1.1**: Text alternatives for images and media
- **1.2**: Captions and alternatives for multimedia
- **1.3**: Adaptable content structure and relationships
- **1.4**: Distinguishable content (contrast, audio control)

### Principle 2: Operable  
- **2.1**: Keyboard accessible functionality
- **2.2**: Enough time for users to read and use content
- **2.3**: Content that does not cause seizures
- **2.4**: Navigable content with clear structure

### Principle 3: Understandable
- **3.1**: Readable and understandable text
- **3.2**: Predictable functionality and navigation
- **3.3**: Input assistance and error prevention

### Principle 4: Robust
- **4.1**: Compatible with assistive technologies
- **4.2**: Valid, semantic markup and code

## 🔧 Implementation Best Practices

### Evaluation Process
1. **Audit Analysis**: Thorough review of accessibility audit findings
2. **Plan Assessment**: Detailed evaluation using weighted criteria
3. **Cross-validation**: Multiple judge evaluation for reliability
4. **Consensus Building**: Automated resolution of scoring differences
5. **Final Recommendation**: Clear implementation guidance

### Quality Assurance
- **Consistency**: Standardized evaluation criteria across all plans
- **Objectivity**: Evidence-based scoring with detailed reasoning
- **Transparency**: Clear documentation of evaluation methodology
- **Reliability**: Multiple judge validation and consensus mechanisms

## 🔗 Related Documentation

- **[API Reference](../api-reference/agents-api.md)** - Agent implementation details
- **[Examples](../examples/basic-usage.md)** - Evaluation workflow examples  
- **[Architecture](../architecture/system-overview.md)** - System design overview
