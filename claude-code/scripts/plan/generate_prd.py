#!/usr/bin/env python3
"""
PRD Template Generator
Generates comprehensive Product Requirements Documents from JSON input data.
"""

import json
import sys
import argparse
from typing import Dict, List, Any


def generate_prd_content(data: Dict[str, Any]) -> str:
    """Generate PRD markdown content from structured data."""

    def format_features(features: List[Dict[str, str]], category: str) -> str:
        """Format features for a specific MoSCoW category."""
        if not features:
            return f"_No {category.lower()} features defined_\n"

        content = ""
        for feature in features:
            content += f"- **{feature['name']}** - {feature['description']}\n"
        return content

    def format_personas(personas: List[Dict[str, Any]]) -> str:
        """Format user personas."""
        if not personas:
            return "_No personas defined_\n"

        content = ""
        for persona in personas:
            content += f"### {persona['name']} - {persona['role']}\n\n"
            content += "**Demographics:**\n\n"
            for key, value in persona.get("demographics", {}).items():
                content += f"- {key.title()}: {value}\n"

            content += "\n**Context & Goals:**\n\n"
            for key, value in persona.get("context", {}).items():
                content += f"- **{key.replace('_', ' ').title()}:** {value}\n"

            content += "\n**Pain Points:**\n\n"
            for pain_point in persona.get("pain_points", []):
                content += (
                    f"- **{pain_point['category']}:** \"{pain_point['quote']}\"\n"
                )

            content += "\n**Screen Usage Patterns:**\n\n"
            patterns = persona.get("screen_patterns", {})
            for key, value in patterns.items():
                content += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            content += "\n"

        return content

    def format_screens(screens: List[Dict[str, str]], category: str) -> str:
        """Format screen inventory."""
        if not screens:
            return f"_No {category.lower()} screens defined_\n"

        content = ""
        for screen in screens:
            content += f"- **{screen['name']}:** {screen['description']}\n"
        return content

    def format_design_principles(principles: Dict[str, Any]) -> str:
        """Format design principles section."""
        content = "### Core Design Principles\n\n"

        if "usability" in principles:
            content += "**Usability Principles:**\n\n"
            for principle in principles["usability"]:
                content += f"- **{principle['name']}:** {principle['description']}\n"
            content += "\n"

        if "accessibility" in principles:
            content += "**Accessibility Standards:**\n\n"
            for standard in principles["accessibility"]:
                content += (
                    f"- **{standard['requirement']}:** {standard['specification']}\n"
                )
            content += "\n"

        return content

    # Build PRD content
    prd_content = f"""# {data['product_name']}: {data['brief_description']}

## Product Requirements Document v1.0

---

## 1. Project Overview

{data.get('overview', 'Product overview not provided.')}

---

## 2. MoSCoW Prioritised Features

### Must Have

{format_features(data.get('features', {}).get('must_have', []), 'Must Have')}

### Should Have

{format_features(data.get('features', {}).get('should_have', []), 'Should Have')}

### Could Have

{format_features(data.get('features', {}).get('could_have', []), 'Could Have')}

### Won't Have

{format_features(data.get('features', {}).get('wont_have', []), "Won't Have")}

---

## 3. Design Principles & Guidelines

{format_design_principles(data.get('design_principles', {}))}

### Visual Design Guidelines

{data.get('visual_guidelines', '_Visual design guidelines not specified._')}

### Interaction Design Standards

{data.get('interaction_standards', '_Interaction design standards not specified._')}

### Platform-Specific Design Considerations

{data.get('platform_considerations', '_Platform-specific considerations not specified._')}

### Design System References

{data.get('design_system', '_Design system references not specified._')}

---

## 4. Screen Inventory & Information Architecture

### Screen Overview

**Primary Screens:**

{format_screens(data.get('screens', {}).get('primary', []), 'Primary')}

**Secondary/Supporting Screens:**

{format_screens(data.get('screens', {}).get('secondary', []), 'Secondary')}

**Administrative/Configuration Screens:**

{format_screens(data.get('screens', {}).get('admin', []), 'Administrative')}

### Feature-to-Screen Mapping

{data.get('screen_mapping', '_Feature-to-screen mapping not provided._')}

### User Flow Architecture

{data.get('user_flows', '_User flow architecture not provided._')}

### Screen Hierarchy & Relationships

{data.get('screen_hierarchy', '_Screen hierarchy and relationships not provided._')}

---

## 5. Detailed Feature Specifications

### Must Have Features

{data.get('detailed_features', '_Detailed feature specifications not provided._')}

---

## 6. Target Users and Their Motivations

{format_personas(data.get('personas', []))}

---

## 7. Onboarding Experience Design

### Core Onboarding Principles

{data.get('onboarding_principles', '_Onboarding principles not specified._')}

### Onboarding Architecture

{data.get('onboarding_architecture', '_Onboarding architecture not specified._')}

### Platform-Specific Considerations

{data.get('onboarding_platforms', '_Platform-specific onboarding considerations not specified._')}

---

## Quality Gates

### Content Quality Standards

- **Specificity:** Every feature specification must include concrete, actionable details
- **User-Centricity:** All features must clearly connect to user needs and pain points
- **UX Precision:** UX requirements must be specific enough for design teams
- **UX Focus:** Interface and interaction specifications must be detailed and comprehensive
- **Design Consistency:** Design principles must guide all feature implementations
- **Screen Architecture Clarity:** All screens must map clearly to features and user flows with explicit relationships documented
- **User Flow Completeness:** All identified user journeys must be fully mapped across screens with clear entry and exit points
- **Onboarding Excellence:** First-time user experience must balance immediate value with necessary setup

### Section Completion Requirements

- **No placeholder text:** Every section must contain real, contextual content
- **Consistent detail level:** Maintain thorough detail across all feature specifications
- **Complete screen mapping:** Every feature must be mapped to specific screens with clear interaction patterns
- **Flow documentation:** All user paths between screens must be explicitly documented

### Template Adaptation Guidelines

- **Maintain structure:** Keep all section headings and overall organisation
- **Adapt content depth:** Scale detail level based on product complexity
- **Preserve user focus:** Ensure UX/UI considerations remain prominent throughout
- **Include complete specifications:** Don't summarise or abbreviate critical details
- **Screen-feature integration:** Ensure clear relationships between features and screen architecture

Remember: The goal is to create a PRD document that serves as a definitive guide for product feature development, with particular emphasis on user experience design, interface specifications, and clear screen architecture that supports optimal user flows.
"""

    return prd_content


def main():
    parser = argparse.ArgumentParser(description="Generate PRD from JSON data")
    parser.add_argument("json_file", help="Path to JSON file containing PRD data")
    parser.add_argument(
        "-o", "--output", help="Output file path (default: [product_name].md)"
    )
    parser.add_argument(
        "--output-format",
        choices=["markdown"],
        default="markdown",
        help="Output format (default: markdown)",
    )

    args = parser.parse_args()

    try:
        # Read JSON data
        with open(args.json_file, "r") as f:
            data = json.load(f)

        # Generate PRD content
        prd_content = generate_prd_content(data)

        # Determine output file
        if args.output:
            output_file = args.output
        else:
            product_name = data.get("product_name", "product").lower().replace(" ", "_")
            output_file = f"{product_name}.md"

        # Write PRD file
        with open(output_file, "w") as f:
            f.write(prd_content)

        print(f"PRD generated successfully: {output_file}")

    except FileNotFoundError:
        print(f"Error: JSON file '{args.json_file}' not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{args.json_file}': {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
