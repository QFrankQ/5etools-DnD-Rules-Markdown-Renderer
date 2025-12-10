/**
 * Simple Rendering Service for 5etools Data
 * Converts JSON entries to Markdown for RAG/Vector DB embedding
 */

// Load required dependencies
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Mock browser globals that 5etools expects
global.window = {
    addEventListener: () => {},
    removeEventListener: () => {},
    location: { origin: '', href: '', hostname: 'localhost' },
    localStorage: {
        getItem: () => null,
        setItem: () => {},
        removeItem: () => {}
    }
};
global.document = {
    createElement: () => ({ style: {} }),
    querySelectorAll: () => []
};
global.navigator = { userAgent: 'node' };
global.location = { origin: '', href: '', hostname: 'localhost' };
global.localStorage = global.window.localStorage;
global.DEPLOYED_IMG_ROOT = '';

// Mock VetoolsConfig
global.VetoolsConfig = {
    get: (category, key) => {
        if (category === 'styleSwitcher' && key === 'style') return 'classic';
        return null;
    }
};

// Mock jQuery and other UI utilities
global.$ = (selector) => {
    let htmlContent = '';

    const mockElement = {
        toggle: () => mockElement,
        remove: () => mockElement,
        html: function(content) {
            // If called with any arguments (even undefined), it's a setter
            if (arguments.length > 0) {
                htmlContent = content || '';
                return mockElement;
            }
            // No arguments = getter
            return htmlContent;
        },
        text: function(content) {
            // If called with any arguments (even undefined), it's a setter
            if (arguments.length > 0) {
                htmlContent = content || '';
                return mockElement;
            }
            // No arguments = getter - extract text from HTML by removing tags
            return htmlContent.replace(/<[^>]*>/g, '');
        },
        append: () => mockElement,
        addClass: () => mockElement,
        removeClass: () => mockElement,
        attr: () => mockElement,
        prop: () => mockElement,
        val: () => '',
    };
    return mockElement;
};

// UiUtil - UI utility functions
global.UiUtil = {
    getEnumColoredName: () => '',
    intToBonus: (int, {isPretty = false} = {}) => {
        return `${int >= 0 ? "+" : int < 0 ? (isPretty ? "\u2212" : "-") : ""}${Math.abs(int)}`;
    },
    strToInt: (str, fallback = 0, opts = {}) => {
        const int = parseInt(str);
        return isNaN(int) ? fallback : int;
    },
};

// PrereleaseUtil - for prerelease content
global.PrereleaseUtil = {
    hasSourceJson: () => false,
    getBrewProcessedFromCache: (prop) => [],
};

// BrewUtil2 - for homebrew content
global.BrewUtil2 = {
    hasSourceJson: () => false,
    getBrewProcessedFromCache: (prop) => [],
};

// Load 5etools modules in correct order
await import('./js/parser.js');
await import('./js/utils.js');
// await import('./js/utils-dataloader.js');
await import('./js/render.js');
await import('./js/render-markdown.js');

/**
 * Rendering Service Class
 */
class RenderingService {
    constructor() {
        this.dataDir = path.join(__dirname, 'data');
        this.outputDir = path.join(__dirname, 'markdown-output');
        this.metadataDir = path.join(__dirname, 'metadata-output');

        // Ensure output directories exist
        if (!fs.existsSync(this.outputDir)) {
            fs.mkdirSync(this.outputDir, { recursive: true });
        }
        if (!fs.existsSync(this.metadataDir)) {
            fs.mkdirSync(this.metadataDir, { recursive: true });
        }

        // Map of entity types to their data files and JSON property names
        this.entityTypeMap = {
            spell: { files: ['spells/spells-phb.json', 'spells/spells-xge.json'], prop: 'spell' },
            item: { files: ['items.json'], prop: 'item' },
            monster: { files: ['bestiary/bestiary-mm.json'], prop: 'monster' },
            action: { files: ['actions.json'], prop: 'action' },
            feat: { files: ['feats.json'], prop: 'feat' },
            race: { files: ['races.json'], prop: 'race' },
            background: { files: ['backgrounds.json'], prop: 'background' },
            condition: { files: ['conditionsdiseases.json'], prop: 'condition' },
            disease: { files: ['conditionsdiseases.json'], prop: 'disease' },
            variantrule: { files: ['variantrules.json'], prop: 'variantrule' },
            deity: { files: ['deities.json'], prop: 'deity' },
            language: { files: ['languages.json'], prop: 'language' },
            object: { files: ['objects.json'], prop: 'object' },
            trap: { files: ['trapshazards.json'], prop: 'trap' },
            hazard: { files: ['trapshazards.json'], prop: 'hazard' },
            reward: { files: ['rewards.json'], prop: 'reward' },
            psionic: { files: ['psionics.json'], prop: 'psionic' },
            recipe: { files: ['recipes.json'], prop: 'recipe' },
            vehicle: { files: ['vehicles.json'], prop: 'vehicle' },
            optionalfeature: { files: ['optionalfeatures.json'], prop: 'optionalfeature' },
            sense: { files: ['senses.json'], prop: 'sense' },
        };
    }

    /**
     * Load JSON data from a file
     */
    loadData(filePath) {
        const fullPath = path.join(this.dataDir, filePath);
        if (!fs.existsSync(fullPath)) {
            console.warn(`File not found: ${fullPath}`);
            return null;
        }

        const data = fs.readFileSync(fullPath, 'utf8');
        return JSON.parse(data);
    }

    /**
     * Render a single entry to markdown
     */
    renderEntry(entry, entityType) {
        try {
            // Enhance items before rendering (adds _attunement, _typeHtml, etc.)
            if (entityType === 'item' && Renderer.item && Renderer.item.enhanceItem) {
                Renderer.item.enhanceItem(entry);
            }

            const rendererClass = RendererMarkdown[entityType];

            if (!rendererClass || !rendererClass.getCompactRenderedString) {
                // Use generic fallback renderer for types without specific renderer
                return this._renderGeneric(entry, entityType);
            }

            // Initialize meta with required properties for rendering
            const meta = {
                _typeStack: [],
                depth: 0
            };

            const markdown = rendererClass.getCompactRenderedString(entry, {
                meta: meta
            });

            return markdown;
        } catch (error) {
            console.error(`Error rendering ${entityType}:`, error.message);
            return null;
        }
    }

    /**
     * Generic fallback renderer for entity types without a specific renderer
     */
    _renderGeneric(entry, entityType) {
        const parts = [];

        // Title
        if (entry.name) {
            parts.push(`## ${entry.name}`);
            parts.push('');
        }

        // Render entries content
        if (entry.entries && Array.isArray(entry.entries)) {
            const meta = { _typeStack: [], depth: 0 };
            const textStack = [''];

            const renderer = RendererMarkdown.get();
            for (const ent of entry.entries) {
                renderer.recursiveRender(ent, textStack, meta);
            }

            parts.push(textStack.join('').trim());
        }

        return parts.join('\n');
    }

    /**
     * Render all entries of a specific type
     */
    renderType(entityType, options = {}) {
        const { limit = null, saveToFile = true, silent = false } = options;

        const config = this.entityTypeMap[entityType];
        if (!config) {
            if (!silent) console.error(`Unknown entity type: ${entityType}`);
            return [];
        }

        const results = [];
        let totalProcessed = 0;

        for (const dataFile of config.files) {
            const data = this.loadData(dataFile);
            if (!data || !data[config.prop]) {
                continue;
            }

            const entries = data[config.prop];
            const entriesToProcess = limit ? entries.slice(0, limit - totalProcessed) : entries;

            if (!silent) {
                console.log(`Processing ${entriesToProcess.length} ${entityType}(s) from ${dataFile}...`);
            }

            for (const entry of entriesToProcess) {
                const markdown = this.renderEntry(entry, entityType);

                if (markdown) {
                    results.push({
                        name: entry.name || entry._displayName || 'Unknown',
                        source: entry.source || 'Unknown',
                        markdown: markdown,
                        metadata: this.extractMetadata(entry, entityType, dataFile)
                    });
                }

                totalProcessed++;
                if (limit && totalProcessed >= limit) break;
            }

            if (limit && totalProcessed >= limit) break;
        }

        // Save to file if requested
        if (saveToFile && results.length > 0) {
            this.saveResults(entityType, results, silent);
        }

        return results;
    }

    /**
     * Save rendered results to files
     */
    saveResults(entityType, results, silent = false) {
        const typeDir = path.join(this.outputDir, entityType);
        if (!fs.existsSync(typeDir)) {
            fs.mkdirSync(typeDir, { recursive: true });
        }

        // Save individual markdown files
        results.forEach((result, index) => {
            const filename = `${this.sanitizeFilename(result.name)}_${result.source}.md`;
            const filePath = path.join(typeDir, filename);

            // Add minimal metadata header (just name and type)
            const content = `---
name: ${result.name}
type: ${entityType}
---

${result.markdown}`;

            fs.writeFileSync(filePath, content);
        });

        // Save combined file
        const combinedPath = path.join(typeDir, `_all_${entityType}s.md`);
        const combinedContent = results.map(r => r.markdown).join('\n\n---\n\n');
        fs.writeFileSync(combinedPath, combinedContent);

        // Save metadata files as separate JSON files in metadata-output directory
        const metadataTypeDir = path.join(this.metadataDir, entityType);
        if (!fs.existsSync(metadataTypeDir)) {
            fs.mkdirSync(metadataTypeDir, { recursive: true });
        }

        results.forEach((result) => {
            const metaFilename = `${this.sanitizeFilename(result.name)}_${result.source}.json`;
            const metaPath = path.join(metadataTypeDir, metaFilename);
            fs.writeFileSync(metaPath, JSON.stringify(result.metadata, null, 2));
        });

        if (!silent) {
            console.log(`✓ Saved ${results.length} ${entityType}(s) to ${typeDir}`);
            console.log(`✓ Saved ${results.length} metadata files to ${metadataTypeDir}`);
        }
    }

    /**
     * Sanitize filename
     */
    sanitizeFilename(name) {
        return name
            .replace(/[^a-z0-9]/gi, '_')
            .replace(/_+/g, '_')
            .toLowerCase();
    }

    /**
     * Extract metadata from an entry for graph representation
     * OPTIMIZED: Avoids JSON.stringify on large entry.entries arrays
     */
    extractMetadata(entry, entityType, dataFile = null) {
        const metadata = {
            type: entityType,
            name: entry.name,
            source: entry.source,
            page: entry.page,
            file: dataFile,
            references: []
        };

        // 1. Extract inline {@...} tags - OPTIMIZED VERSION
        // Instead of JSON.stringify the entire entries array, we recursively scan
        if (entry.entries && Array.isArray(entry.entries)) {
            this._extractReferencesFromEntries(entry.entries, metadata.references);
        }

        // 2. Extract seeAlso* fields
        const seeAlsoFields = [
            { field: 'seeAlsoAction', tagType: 'action' },
            { field: 'seeAlsoFeature', tagType: 'feature' },
            { field: 'seeAlsoDeck', tagType: 'deck' },
            { field: 'seeAlsoVehicle', tagType: 'vehicle' },
            { field: 'seeAlsoSpell', tagType: 'spell' },
            { field: 'seeAlsoItem', tagType: 'item' }
        ];

        for (const { field, tagType } of seeAlsoFields) {
            if (entry[field] && Array.isArray(entry[field])) {
                entry[field].forEach(ref => {
                    if (typeof ref === 'string') {
                        metadata.references.push({
                            tagType,
                            content: ref,
                            referenceType: field
                        });
                    }
                });
            }
        }

        // 3. Extract variant rule source
        if (entry.fromVariant) {
            metadata.references.push({
                tagType: 'variantrule',
                content: entry.fromVariant,
                referenceType: 'fromVariant'
            });
        }

        // 4. Add type-specific fields
        if (entry.level !== undefined) metadata.level = entry.level;
        if (entry.school) metadata.school = entry.school;
        if (entry.time) metadata.time = entry.time;
        if (entry.rarity) metadata.rarity = entry.rarity;
        if (entry.tier) metadata.tier = entry.tier;
        if (entry.type) {
            if (typeof entry.type === 'string') {
                metadata.itemType = entry.type;
            } else if (typeof entry.type === 'object' && entry.type !== null) {
                metadata.itemType = entry.type;
            }
        }

        return metadata;
    }

    /**
     * Recursively extract {@...} tag references from entries
     * This is MUCH faster than JSON.stringify for large entry arrays
     */
    _extractReferencesFromEntries(entries, references) {
        const tagPattern = /{@(\w+)\s+([^}]+)}/g;

        for (const entry of entries) {
            if (typeof entry === 'string') {
                // Extract tags from string entries
                let match;
                while ((match = tagPattern.exec(entry)) !== null) {
                    references.push({
                        tagType: match[1],
                        content: match[2],
                        referenceType: "inline_tag"
                    });
                }
            } else if (typeof entry === 'object' && entry !== null) {
                // Recursively process nested entries
                if (entry.entries && Array.isArray(entry.entries)) {
                    this._extractReferencesFromEntries(entry.entries, references);
                }
                // Also check 'items' field (used in lists)
                if (entry.items && Array.isArray(entry.items)) {
                    this._extractReferencesFromEntries(entry.items, references);
                }
                // Check string fields that might contain tags
                if (typeof entry.name === 'string') {
                    let match;
                    tagPattern.lastIndex = 0;
                    while ((match = tagPattern.exec(entry.name)) !== null) {
                        references.push({
                            tagType: match[1],
                            content: match[2],
                            referenceType: "inline_tag"
                        });
                    }
                }
            }
        }
    }

    /**
     * Render entries from a specific JSON file
     */
    renderFromFile(filePath, options = {}) {
        const { limit = null, saveToFile = true, silent = false } = options;

        if (!fs.existsSync(filePath)) {
            if (!silent) console.error(`File not found: ${filePath}`);
            return { entityType: null, results: [] };
        }

        const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));

        // Find entity type (first array key)
        let entityType = null;
        let config = null;

        for (const [key, value] of Object.entries(data)) {
            if (Array.isArray(value) && value.length > 0) {
                entityType = key;
                config = this.entityTypeMap[key];
                break;
            }
        }

        if (!entityType || !config) {
            if (!silent) console.error(`No recognized entity type found in ${filePath}`);
            return { entityType: null, results: [] };
        }

        const entries = data[config.prop];
        const entriesToProcess = limit ? entries.slice(0, limit) : entries;

        if (!silent) {
            console.log(`Processing ${entriesToProcess.length} ${entityType}(s) from ${path.basename(filePath)}...`);
        }

        const results = [];

        for (const entry of entriesToProcess) {
            const markdown = this.renderEntry(entry, entityType);

            if (markdown) {
                results.push({
                    name: entry.name || entry._displayName || 'Unknown',
                    source: entry.source || 'Unknown',
                    markdown: markdown,
                    metadata: this.extractMetadata(entry, entityType, path.basename(filePath))
                });
            }
        }

        // Save to file if requested
        if (saveToFile && results.length > 0) {
            this.saveResults(entityType, results, silent);
        }

        return { entityType, results };
    }

    /**
     * Render multiple entity types
     */
    renderMultipleTypes(types, options = {}) {
        const results = {};
        const { silent = false } = options;

        for (const type of types) {
            if (!silent) {
                console.log(`\n=== Rendering ${type.toUpperCase()} ===`);
            }
            results[type] = this.renderType(type, options);
        }

        return results;
    }

    /**
     * Get summary of available data
     */
    getDataSummary() {
        const summary = {};

        for (const [type, config] of Object.entries(this.entityTypeMap)) {
            summary[type] = { files: config.files, count: 0 };

            for (const file of config.files) {
                const data = this.loadData(file);
                if (data && data[config.prop]) {
                    summary[type].count += data[config.prop].length;
                }
            }
        }

        return summary;
    }

    /**
     * Process a request from stdin (for Python integration)
     */
    processStdinRequest() {
        return new Promise((resolve, reject) => {
            let inputData = '';

            process.stdin.on('data', chunk => {
                inputData += chunk;
            });

            process.stdin.on('end', () => {
                try {
                    const request = JSON.parse(inputData);
                    const response = this.handleRequest(request);
                    console.log(JSON.stringify(response));
                    resolve();
                } catch (error) {
                    console.error(JSON.stringify({ error: error.message }));
                    reject(error);
                }
            });
        });
    }

    /**
     * Handle requests from Python
     */
    handleRequest(request) {
        const { action, type, limit, saveToFile, filePath } = request;

        switch (action) {
            case 'summary':
                return { success: true, data: this.getDataSummary() };

            case 'render':
                if (!type) {
                    return { success: false, error: 'Missing type parameter' };
                }
                const results = this.renderType(type, { limit, saveToFile, silent: true });
                return { success: true, data: results };

            case 'render_multiple':
                const types = request.types || [];
                const multiResults = this.renderMultipleTypes(types, { limit, saveToFile, silent: true });
                return { success: true, data: multiResults };

            case 'render_file':
                if (!filePath) {
                    return { success: false, error: 'Missing filePath parameter' };
                }
                const fileResults = this.renderFromFile(filePath, { limit, saveToFile, silent: true });
                return { success: true, data: fileResults };

            default:
                return { success: false, error: `Unknown action: ${action}` };
        }
    }
}

// Export for use as module
export default RenderingService;

// CLI interface - always run when directly executed
const service = new RenderingService();

// Check if reading from stdin (Python integration)
// Use --stdin flag to explicitly request stdin mode, or detect pipe
// On some systems, isTTY detection is unreliable, so we support explicit flag
const hasStdinFlag = process.argv.includes('--stdin');
const isPiped = hasStdinFlag || process.stdin.isTTY === false;

if (isPiped) {
    // Reading JSON from stdin
    await service.processStdinRequest().catch(err => {
        console.error(JSON.stringify({ success: false, error: err.message }));
        process.exit(1);
    });
} else {
    // Normal CLI mode
    console.log('=== 5etools Rendering Service ===\n');

    // Show available data summary
    console.log('Available data:');
    const summary = service.getDataSummary();
    for (const [type, info] of Object.entries(summary)) {
        console.log(`  - ${type}: ${info.count} entries`);
    }

    console.log('\n=== Rendering Sample Entries ===\n');

    // Render samples of different types
    const typesToRender = ['spell', 'action', 'item', 'monster', 'feat'];

    service.renderMultipleTypes(typesToRender, {
        limit: 3,  // Only render 3 of each type for demo
        saveToFile: true
    });

    console.log('\n✓ Done! Check the markdown-output/ directory for results.');
}
