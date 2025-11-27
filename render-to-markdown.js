#!/usr/bin/env node
/**
 * Batch render D&D entries from JSON to Markdown
 *
 * This script processes JSON data files from the 5etools data directory
 * and renders them to markdown format using the RendererMarkdown class.
 */

import fs from "fs";
import path from "path";
import {Command} from "commander";

// Import 5etools modules (these are isomorphic - work in both browser and Node.js)
import "./js/parser.js";
import "./js/utils.js";
import "./js/utils-ui.js";
import "./js/utils-config.js";
import "./js/render.js";
import "./js/render-markdown.js";

const program = new Command()
	.option("-i, --input <file>", "Input JSON file to process")
	.option("-o, --output-dir <dir>", "Output directory for markdown files", "./output")
	.option("-t, --type <type>", "Entry type (spell, item, class, etc.)")
	.option("--all", "Process all data files")
	.option("--list", "List available data files")
;

program.parse(process.argv);
const params = program.opts();

// Helper to ensure output directory exists
function ensureDir(dirPath) {
	if (!fs.existsSync(dirPath)) {
		fs.mkdirSync(dirPath, { recursive: true });
	}
}

// Helper to sanitize filename
function sanitizeFilename(name) {
	return name
		.replace(/[^a-z0-9]/gi, '_')
		.replace(/_+/g, '_')
		.toLowerCase();
}

// Extract tags and metadata from an entry for graph representation
function extractMetadata(entry, entryType) {
	const metadata = {
		type: entryType,
		name: entry.name,
		source: entry.source,
		tags: [],
		references: []
	};

	// Extract tags from entries text
	const entryString = JSON.stringify(entry.entries || []);
	const tagPattern = /{@(\w+)\s+([^}]+)}/g;
	let match;

	while ((match = tagPattern.exec(entryString)) !== null) {
		const tagType = match[1];
		const tagContent = match[2];

		metadata.references.push({
			tagType,
			content: tagContent
		});
	}

	return metadata;
}

// Render a single entry to markdown
function renderEntryToMarkdown(entry, entryType) {
	const renderer = RendererMarkdown.get();
	const renderStack = [];

	// Set up rendering metadata
	const meta = {
		depth: 0,
		_typeStack: []
	};

	// Reset renderer state
	renderer.setFirstSection(true);
	renderer.resetHeaderIndex();

	// Create a wrapper entry with proper structure
	const wrappedEntry = {
		type: "entries",
		name: entry.name,
		entries: entry.entries || []
	};

	// Render the entry
	try {
		renderer.recursiveRender(wrappedEntry, renderStack, meta);
		return renderStack.join("");
	} catch (error) {
		console.error(`Error rendering entry "${entry.name}":`, error.message);
		return `# ${entry.name}\n\n*Error rendering this entry*\n`;
	}
}

// Process a single JSON file
function processFile(filePath, outputDir) {
	console.log(`Processing: ${filePath}`);

	const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
	const basename = path.basename(filePath, '.json');

	// Determine entry type (first array key in the JSON)
	const entryType = Object.keys(data).find(key => Array.isArray(data[key]));

	if (!entryType) {
		console.warn(`No array entries found in ${filePath}`);
		return;
	}

	const entries = data[entryType];
	console.log(`Found ${entries.length} ${entryType} entries`);

	// Create subdirectory for this entry type
	const typeDir = path.join(outputDir, entryType);
	ensureDir(typeDir);

	// Create metadata directory
	const metadataDir = path.join(outputDir, 'metadata', entryType);
	ensureDir(metadataDir);

	// Process each entry
	let successCount = 0;
	let errorCount = 0;

	for (const entry of entries) {
		try {
			// Render to markdown
			const markdown = renderEntryToMarkdown(entry, entryType);

			// Extract metadata
			const metadata = extractMetadata(entry, entryType);

			// Generate filename
			const filename = sanitizeFilename(entry.name || 'unnamed');
			const source = entry.source || 'unknown';
			const fullFilename = `${filename}_${source}.md`;

			// Write markdown file
			const mdPath = path.join(typeDir, fullFilename);
			fs.writeFileSync(mdPath, markdown, 'utf8');

			// Write metadata file
			const metaPath = path.join(metadataDir, `${filename}_${source}.json`);
			fs.writeFileSync(metaPath, JSON.stringify(metadata, null, 2), 'utf8');

			successCount++;
		} catch (error) {
			console.error(`Error processing entry "${entry.name}":`, error.message);
			errorCount++;
		}
	}

	console.log(`Completed: ${successCount} successful, ${errorCount} errors\n`);
}

// List all available data files
function listDataFiles() {
	const dataDir = './data';
	const files = fs.readdirSync(dataDir)
		.filter(file => file.endsWith('.json') && !file.startsWith('fluff-'))
		.sort();

	console.log('\nAvailable data files:');
	files.forEach(file => console.log(`  - ${file}`));
	console.log('');
}

// Main execution
async function main() {
	if (params.list) {
		listDataFiles();
		return;
	}

	ensureDir(params.outputDir);

	if (params.input) {
		// Process single file
		const inputPath = path.resolve(params.input);
		processFile(inputPath, params.outputDir);
	} else if (params.all) {
		// Process all data files
		const dataDir = './data';
		const files = fs.readdirSync(dataDir)
			.filter(file => file.endsWith('.json') && !file.startsWith('fluff-'))
			.map(file => path.join(dataDir, file));

		console.log(`Processing ${files.length} data files...\n`);

		for (const file of files) {
			try {
				processFile(file, params.outputDir);
			} catch (error) {
				console.error(`Error processing ${file}:`, error.message);
			}
		}

		console.log('All files processed!');
	} else {
		console.error('Please specify --input <file> or --all');
		program.help();
	}
}

main().catch(console.error);
