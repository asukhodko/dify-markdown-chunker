# Career Development Matrix

## Overview

This document outlines the career development framework for engineering roles at our company. It provides clear expectations for each level and guidance for career progression.

## Engineering Levels

### Junior Engineer (L1)

#### Technical Skills
- Basic understanding of programming fundamentals
- Familiarity with version control (Git)
- Ability to write simple unit tests
- Understanding of basic data structures

#### Responsibilities
- Complete assigned tasks with guidance
- Participate in code reviews
- Learn team processes and tools
- Ask questions and seek feedback

#### Growth Areas
- Develop debugging skills
- Learn to estimate task complexity
- Build domain knowledge

### Mid-Level Engineer (L2)

#### Technical Skills
- Proficient in primary programming language
- Understanding of system design basics
- Ability to write comprehensive tests
- Knowledge of CI/CD pipelines

#### Responsibilities
- Complete tasks independently
- Mentor junior engineers
- Contribute to technical discussions
- Write technical documentation

#### Growth Areas
- Lead small projects
- Improve code review skills
- Develop cross-team collaboration

### Senior Engineer (L3)

#### Technical Skills
- Expert in multiple programming languages
- Strong system design capabilities
- Performance optimization skills
- Security best practices knowledge

#### Responsibilities
- Lead technical projects
- Define technical standards
- Review architecture decisions
- Guide team technical direction

#### Growth Areas
- Strategic thinking
- Cross-functional leadership
- Technical vision development

## Promotion Criteria

### From L1 to L2

| Criteria | Description |
|----------|-------------|
| Technical | Demonstrates proficiency in core technologies |
| Impact | Consistently delivers quality work |
| Collaboration | Works effectively with team members |
| Growth | Shows continuous learning and improvement |

### From L2 to L3

| Criteria | Description |
|----------|-------------|
| Technical | Shows expertise and innovation |
| Impact | Delivers significant business value |
| Leadership | Mentors others effectively |
| Influence | Shapes technical decisions |

## Resources

### Learning Paths

For more information, visit our internal wiki:
- [Engineering Handbook](https://wiki.company.com/engineering)
- [Technical Training](https://learn.company.com/tech)
- [Career Framework](https://hr.company.com/careers)

### Contact

Questions? Reach out to:
- Email: careers@company.com
- Slack: #career-development
- Manager: Schedule a 1:1

## Appendix

### Code Examples

Here's an example of good code documentation:

```python
def calculate_level_score(metrics: dict) -> int:
    """
    Calculate the overall level score based on performance metrics.
    
    Args:
        metrics: Dictionary containing performance data
        
    Returns:
        Integer score from 0-100
    """
    weights = {
        'technical': 0.4,
        'impact': 0.3,
        'collaboration': 0.2,
        'growth': 0.1
    }
    
    total = sum(
        metrics.get(key, 0) * weight 
        for key, weight in weights.items()
    )
    return int(total * 100)
```

### Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01-01 | Initial release |
| 1.1 | 2024-03-15 | Added L3 criteria |
| 1.2 | 2024-06-01 | Updated resources |
