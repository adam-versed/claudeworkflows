#!/usr/bin/env python3
"""
Component overlap detection for monorepo projects.
Identifies and resolves duplicate monitoring components to prevent log duplication and port conflicts.
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional

def detect_monorepo_tools(project_path: Path) -> Dict[str, Any]:
    """Detect monorepo orchestration tools and their configurations."""
    monorepo_info = {
        "detected": False,
        "tools": [],
        "config_files": [],
        "workspace_config": None
    }
    
    # Check for Turborepo
    turbo_json = project_path / "turbo.json"
    if turbo_json.exists():
        monorepo_info["detected"] = True
        monorepo_info["tools"].append("turborepo")
        monorepo_info["config_files"].append(str(turbo_json))
        try:
            with open(turbo_json, 'r') as f:
                monorepo_info["workspace_config"] = {"turborepo": json.load(f)}
        except:
            pass
    
    # Check for Lerna
    lerna_json = project_path / "lerna.json"
    if lerna_json.exists():
        monorepo_info["detected"] = True
        monorepo_info["tools"].append("lerna")
        monorepo_info["config_files"].append(str(lerna_json))
        try:
            with open(lerna_json, 'r') as f:
                if "workspace_config" not in monorepo_info:
                    monorepo_info["workspace_config"] = {}
                monorepo_info["workspace_config"]["lerna"] = json.load(f)
        except:
            pass
    
    # Check for Nx
    nx_json = project_path / "nx.json"
    if nx_json.exists():
        monorepo_info["detected"] = True
        monorepo_info["tools"].append("nx")
        monorepo_info["config_files"].append(str(nx_json))
        try:
            with open(nx_json, 'r') as f:
                if "workspace_config" not in monorepo_info:
                    monorepo_info["workspace_config"] = {}
                monorepo_info["workspace_config"]["nx"] = json.load(f)
        except:
            pass
    
    # Check for Rush
    rush_json = project_path / "rush.json"
    if rush_json.exists():
        monorepo_info["detected"] = True
        monorepo_info["tools"].append("rush")
        monorepo_info["config_files"].append(str(rush_json))
    
    # Check for Yarn workspaces
    package_json = project_path / "package.json"
    if package_json.exists():
        try:
            with open(package_json, 'r') as f:
                pkg = json.load(f)
                if "workspaces" in pkg:
                    monorepo_info["detected"] = True
                    monorepo_info["tools"].append("yarn-workspaces")
                    if "workspace_config" not in monorepo_info:
                        monorepo_info["workspace_config"] = {}
                    monorepo_info["workspace_config"]["yarn"] = pkg.get("workspaces", [])
        except:
            pass
    
    # Check for pnpm workspaces
    pnpm_workspace = project_path / "pnpm-workspace.yaml"
    if pnpm_workspace.exists():
        monorepo_info["detected"] = True
        monorepo_info["tools"].append("pnpm-workspaces")
        monorepo_info["config_files"].append(str(pnpm_workspace))
    
    return monorepo_info

def analyze_command_patterns(components: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Group components by their command patterns to identify overlaps."""
    patterns = {
        "global_orchestrator": [],  # turbo run dev, lerna run dev, etc.
        "individual_components": [],  # npm run dev in specific directories
        "standalone_services": []  # docker, external services, etc.
    }
    
    for component in components:
        name = component.get("name", "")
        start_command = component.get("start_command", "")
        cwd = component.get("cwd", ".")
        
        # Detect global orchestrator commands
        if any(cmd in start_command.lower() for cmd in ["turbo run", "lerna run", "nx run", "rush", "yarn workspaces"]):
            patterns["global_orchestrator"].append(component)
        # Detect individual component commands
        elif any(cmd in start_command.lower() for cmd in ["npm run", "yarn run", "pnpm run", "bun run"]) or \
             any(framework in start_command.lower() for framework in ["next dev", "vite", "convex dev", "fastapi", "flask run"]):
            patterns["individual_components"].append(component)
        # Everything else is standalone
        else:
            patterns["standalone_services"].append(component)
    
    return patterns

def detect_component_overlaps(components: List[Dict[str, Any]], project_path: str = ".") -> Dict[str, Any]:
    """Detect overlapping components that would cause duplicate processes."""
    project_path = Path(project_path)
    
    # Detect monorepo setup
    monorepo_info = detect_monorepo_tools(project_path)
    
    # Analyze command patterns
    command_patterns = analyze_command_patterns(components)
    
    overlaps = {
        "detected": False,
        "issues": [],
        "recommendations": [],
        "monorepo_info": monorepo_info,
        "command_patterns": command_patterns
    }
    
    # Check for overlaps between global orchestrator and individual components
    if command_patterns["global_orchestrator"] and command_patterns["individual_components"]:
        overlaps["detected"] = True
        
        global_commands = [comp["name"] for comp in command_patterns["global_orchestrator"]]
        individual_commands = [comp["name"] for comp in command_patterns["individual_components"]]
        
        overlaps["issues"].append({
            "type": "monorepo_duplication",
            "description": f"Both global orchestrator ({', '.join(global_commands)}) and individual components ({', '.join(individual_commands)}) detected",
            "impact": "This will cause duplicate processes and conflicting log entries",
            "example_conflict": "Multiple instances of the same service running on different ports"
        })
        
        # Recommend strategy based on detected commands and monorepo tool
        # Check if we have turbo commands (even without turbo.json)
        has_turbo_commands = any("turbo run" in comp.get("start_command", "") for comp in command_patterns["global_orchestrator"])
        has_lerna_commands = any("lerna run" in comp.get("start_command", "") for comp in command_patterns["global_orchestrator"])
        
        if monorepo_info["detected"] and "turborepo" in monorepo_info["tools"]:
            overlaps["recommendations"].append({
                "strategy": "prefer_individual_components",
                "reason": "Turborepo components can be started individually for better log attribution",
                "action": "Remove global 'turbo run dev' command, keep individual component commands",
                "components_to_remove": [comp["name"] for comp in command_patterns["global_orchestrator"]],
                "components_to_keep": [comp["name"] for comp in command_patterns["individual_components"]]
            })
        elif has_turbo_commands:
            # Turbo commands detected without turbo.json - still prefer individual components
            overlaps["recommendations"].append({
                "strategy": "prefer_individual_components",
                "reason": "Turborepo detected - individual components provide better log attribution than global 'turbo run dev'",
                "action": "Remove global 'turbo run dev' command, keep individual component commands",
                "components_to_remove": [comp["name"] for comp in command_patterns["global_orchestrator"]],
                "components_to_keep": [comp["name"] for comp in command_patterns["individual_components"]]
            })
        elif monorepo_info["detected"] and "lerna" in monorepo_info["tools"]:
            overlaps["recommendations"].append({
                "strategy": "prefer_global_orchestrator", 
                "reason": "Lerna typically requires coordinated startup",
                "action": "Remove individual component commands, keep global 'lerna run dev'",
                "components_to_remove": [comp["name"] for comp in command_patterns["individual_components"]],
                "components_to_keep": [comp["name"] for comp in command_patterns["global_orchestrator"]]
            })
        elif has_lerna_commands:
            # Lerna commands detected - prefer global orchestrator
            overlaps["recommendations"].append({
                "strategy": "prefer_global_orchestrator", 
                "reason": "Lerna detected - typically requires coordinated startup",
                "action": "Remove individual component commands, keep global 'lerna run dev'",
                "components_to_remove": [comp["name"] for comp in command_patterns["individual_components"]],
                "components_to_keep": [comp["name"] for comp in command_patterns["global_orchestrator"]]
            })
        else:
            # Default to individual components for better monitoring
            overlaps["recommendations"].append({
                "strategy": "prefer_individual_components",
                "reason": "Individual components provide better log attribution and monitoring",
                "action": "Remove global orchestrator commands, keep individual component commands",
                "components_to_remove": [comp["name"] for comp in command_patterns["global_orchestrator"]],
                "components_to_keep": [comp["name"] for comp in command_patterns["individual_components"]]
            })
    
    # Check for port conflicts
    ports_used = {}
    for component in components:
        port = component.get("port")
        if port:
            if port in ports_used:
                overlaps["detected"] = True
                overlaps["issues"].append({
                    "type": "port_conflict",
                    "description": f"Port {port} used by both '{ports_used[port]}' and '{component['name']}'",
                    "impact": "Services will fail to start or conflict with each other",
                    "components": [ports_used[port], component["name"]]
                })
            else:
                ports_used[port] = component["name"]
    
    return overlaps

def resolve_overlaps(components: List[Dict[str, Any]], overlaps: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Apply overlap resolution recommendations to component list."""
    if not overlaps["detected"]:
        return components
    
    resolved_components = components.copy()
    
    for recommendation in overlaps["recommendations"]:
        if recommendation["strategy"] == "prefer_individual_components":
            # Remove global orchestrator components
            components_to_remove = set(recommendation["components_to_remove"])
            resolved_components = [
                comp for comp in resolved_components 
                if comp["name"] not in components_to_remove
            ]
        elif recommendation["strategy"] == "prefer_global_orchestrator":
            # Remove individual component commands
            components_to_remove = set(recommendation["components_to_remove"])
            resolved_components = [
                comp for comp in resolved_components 
                if comp["name"] not in components_to_remove
            ]
    
    return resolved_components

def main():
    parser = argparse.ArgumentParser(description="Detect and resolve component overlaps in monitoring setup")
    parser.add_argument("--components", required=True, help="JSON string of component configurations")
    parser.add_argument("--project-path", default=".", help="Path to project root")
    parser.add_argument("--resolve", action="store_true", help="Apply resolution recommendations")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    
    args = parser.parse_args()
    
    try:
        components = json.loads(args.components)
    except json.JSONDecodeError as e:
        print(f"Error parsing components JSON: {e}")
        return 1
    
    if not isinstance(components, list):
        print("Components must be a JSON array")
        return 1
    
    # Detect overlaps
    overlaps = detect_component_overlaps(components, args.project_path)
    
    result = {
        "overlaps_detected": overlaps["detected"],
        "original_components": components,
        "overlap_analysis": overlaps
    }
    
    if args.resolve and overlaps["detected"]:
        resolved_components = resolve_overlaps(components, overlaps)
        result["resolved_components"] = resolved_components
        result["components_removed"] = len(components) - len(resolved_components)
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        # Human-readable output
        print(f"Component Overlap Analysis")
        print(f"========================")
        print(f"Project Path: {args.project_path}")
        print(f"Components Analyzed: {len(components)}")
        print()
        
        if overlaps["detected"]:
            print("⚠️  OVERLAPS DETECTED")
            print()
            
            for issue in overlaps["issues"]:
                print(f"Issue Type: {issue['type']}")
                print(f"Description: {issue['description']}")
                print(f"Impact: {issue['impact']}")
                print()
            
            print("Recommendations:")
            for i, rec in enumerate(overlaps["recommendations"], 1):
                print(f"{i}. {rec['strategy'].replace('_', ' ').title()}")
                print(f"   Reason: {rec['reason']}")
                print(f"   Action: {rec['action']}")
                if 'components_to_remove' in rec:
                    print(f"   Remove: {', '.join(rec['components_to_remove'])}")
                if 'components_to_keep' in rec:
                    print(f"   Keep: {', '.join(rec['components_to_keep'])}")
                print()
            
            if args.resolve:
                resolved_components = resolve_overlaps(components, overlaps)
                print(f"Resolution Applied:")
                print(f"  Original components: {len(components)}")
                print(f"  Resolved components: {len(resolved_components)}")
                print(f"  Components removed: {len(components) - len(resolved_components)}")
        else:
            print("✅ No overlaps detected")
            print("All components appear to be properly isolated.")
    
    return 0

if __name__ == "__main__":
    exit(main())