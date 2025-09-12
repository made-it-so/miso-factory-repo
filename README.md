# MISO (Made-It-So) ??

## Overview
MISO is an expert AI assistant designed to function as a strategic partner in creating and analyzing software. It operates on a **Simplicity Mandate**, providing an intuitive conversational interface to control a complex, multi-agent system.

## Current Status: Stable v0.2
The MISO Cockpit is now stable and operational. Current, fully tested features include:
- **Intelligent Creative Dialogue:** A dynamic, history-aware conversational agent (`UIAgent`) that helps users define complex project ideas from scratch.
- **Code Analysis (`OntologyAgent`):** The ability to analyze a directory of source code (`analyze <path>`) and generate a text-based summary.
- **Interactive Visualization (`Cartographer`):** A "Living Blueprint" that displays an interactive, clickable mind map of the analyzed code structure.
- **Conversational Exploration:** The ability to ask for details about specific code elements by clicking on the mind map (`Click-to-Explain`).

## How to Run
This project is fully containerized. The most reliable launch procedure is a two-step, no-cache build:
1. Ensure Docker Desktop is running.
2. From the project root, run: `docker-compose build --no-cache`
3. Then, run: `docker-compose up`
4. The MISO Cockpit will be available at `http://localhost:80`.
