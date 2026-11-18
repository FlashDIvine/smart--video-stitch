#!/usr/bin/env node
/**
 * TikTok Studio CDP Automated Publisher
 * Part of smart-video-stitch pipeline.
 *
 * Automates uploading and publishing video files to TikTok Studio via Chrome/Brave
 * DevTools Protocol (CDP) on port 9222.
 *
 * Usage:
 *   node scripts/tiktok_uploader.js --file /path/to/video.mp4 --caption "Video Title #fyp"
 *   node scripts/tiktok_uploader.js --file /path/to/video.mp4 --caption-file /path/to/caption.txt
 */

const fs = require('fs');
const path = require('path');

// Flexible Playwright resolver
function resolvePlaywright() {
    const candidatePaths = [
        'playwright',
        'playwright-core',
        '/home/najib/Dokumen/Yutub/cat-shorts-pipeline/node_modules/playwright-core',
        path.join(__dirname, '../node_modules/playwright-core'),
        path.join(__dirname, '../node_modules/playwright'),
    ];

    for (const p of candidatePaths) {
        try {
            const mod = require(p);
            if (mod && mod.chromium) return mod.chromium;
        } catch (_) {}
    }
    throw new Error('Playwright not found. Please install via: npm install playwright-core');
}

// Argument parsing helper
function parseArgs() {
    const args = process.argv.slice(2);
    const parsed = {
        file: null,
        caption: '',
        port: 9222,
        json: false,
    };

    for (let i = 0; i < args.length; i++) {
        const arg = args[i];
        if (arg === '--file' || arg === '-f') {
            parsed.file = args[++i];
        } else if (arg === '--caption' || arg === '-c') {
            parsed.caption = args[++i];
        } else if (arg === '--caption-file') {
            const capFile = args[++i];
            if (fs.existsSync(capFile)) {
                parsed.caption = fs.readFileSync(capFile, 'utf8');
            } else {
                console.error(`Caption file not found: ${capFile}`);
            }
        } else if (arg === '--port' || arg === '-p') {
            parsed.port = parseInt(args[++i], 10);
        } else if (arg === '--json') {
            parsed.json = true;
        } else if (arg === '--help' || arg === '-h') {
            printHelp();
            process.exit(0);
        }
    }

    return parsed;
}

function printHelp() {
    console.log(`
TikTok Studio CDP Uploader
--------------------------
Upload and publish videos automatically to TikTok Studio via Chrome/Brave CDP.

Options:
  --file, -f <path>          Path to the video file to upload (required)
  --caption, -c <text>       Caption text with hashtags
  --caption-file <path>      Path to a text file containing the caption
  --port, -p <number>        CDP port (default: 9222)
  --json                     Output result as JSON
  --help, -h                 Show this help message

Requirements:
  1. Brave or Chrome running with: --remote-debugging-port=9222
  2. Already logged into https://www.tiktok.com/tiktokstudio
`);
}

async function removeOverlays(page) {
    await page.evaluate(() => {
        // Remove joyride tour overlay that intercepts pointer events
        document.querySelectorAll('#react-joyride-portal, .react-joyride__overlay').forEach(el => el.remove());

        // Dismiss Tux portal modal if accidentally opened
        const tux = document.querySelector('#tux-portal-container');
        if (tux) {
            const buttons = Array.from(tux.querySelectorAll('button'));
            const cancelBtn = buttons.find(b => {
                const txt = (b.innerText || '').toLowerCase();
                return txt.includes('batal') || txt.includes('cancel');
            });
            if (cancelBtn) cancelBtn.click();
        }
    });
}

async function uploadToTikTok(options) {
    const { file, caption, port, json } = options;

    if (!file) {
        console.error('Error: Video file path (--file) is required.');
        printHelp();
        process.exit(1);
    }

    const resolvedFile = path.resolve(file);
    if (!fs.existsSync(resolvedFile)) {
        console.error(`Error: Video file does not exist: ${resolvedFile}`);
        process.exit(1);
    }

    const chromium = resolvePlaywright();
    const cdpUrl = `http://127.0.0.1:${port}`;

    if (!json) console.log(`🔌 Connecting to browser CDP at ${cdpUrl}...`);
    let browser;
    try {
        browser = await chromium.connectOverCDP(cdpUrl);
    } catch (err) {
        console.error(`❌ Failed to connect to browser CDP at ${cdpUrl}. Is Chrome/Brave running with --remote-debugging-port=${port}?`);
        process.exit(1);
    }

    try {
        const ctx = browser.contexts()[0];
        const pages = ctx.pages();
        let ttPage = pages.find(p => p.url().includes('tiktokstudio') || p.url().includes('tiktok.com'));
        if (!ttPage) {
            ttPage = await ctx.newPage();
        }

        await ttPage.bringToFront();
        if (!json) console.log('🌐 Navigating to TikTok Studio upload page...');
        await ttPage.goto('https://www.tiktok.com/tiktokstudio/upload?from=upload', { waitUntil: 'domcontentloaded' });
        await ttPage.waitForTimeout(3500);

        // Pre-clean joyride overlay
        await removeOverlays(ttPage);

        // 1. Set Video File Input
        if (!json) console.log(`📤 Ingesting video file: ${resolvedFile}`);
        const fileInput = ttPage.locator('input[type="file"][accept*="video"], input[type="file"]').first();
        await fileInput.setInputFiles(resolvedFile);
        if (!json) console.log('⏳ File injected. Waiting for upload processing & thumbnail generation...');
        await ttPage.waitForTimeout(8000);

        // Clean any overlays spawned after upload
        await removeOverlays(ttPage);

        // 2. Set Caption & Hashtags
        if (caption && caption.trim().length > 0) {
            if (!json) console.log('✍️ Writing caption and hashtags...');
            const editor = ttPage.locator('div.notranslate.public-DraftEditor-content, div[contenteditable="true"]').first();
            await editor.click({ force: true });
            await ttPage.waitForTimeout(300);

            // Select all and replace
            await ttPage.keyboard.press('Control+A');
            await ttPage.keyboard.press('Backspace');
            await ttPage.waitForTimeout(200);

            await ttPage.keyboard.insertText(caption);
            if (!json) console.log('✅ Caption set successfully.');
            await ttPage.waitForTimeout(2000);
        }

        // Clean overlays again before post click
        await removeOverlays(ttPage);

        // 3. Click Publish Button
        if (!json) console.log('🚀 Clicking "Posting" button...');
        await ttPage.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
        await ttPage.waitForTimeout(500);

        const postBtn = ttPage.locator('button:has-text("Posting")').last();
        await postBtn.scrollIntoViewIfNeeded();
        await ttPage.waitForTimeout(500);
        await postBtn.click({ force: true });

        if (!json) console.log('⏳ Awaiting publication confirmation & redirect...');
        let isPublished = false;
        let videoUrl = null;

        for (let poll = 0; poll < 15; poll++) {
            await ttPage.waitForTimeout(1000);
            const copyrightModalBtn = ttPage.locator('button:has-text("Posting sekarang"), button:has-text("Post anyway")').first();
            if (await copyrightModalBtn.isVisible().catch(() => false)) {
                if (!json) console.log('⚠️ Copyright check dialog detected. Confirming "Posting sekarang"...');
                await copyrightModalBtn.click({ force: true });
            }

            if (ttPage.url().includes('tiktokstudio/content')) {
                isPublished = true;
                break;
            }
        }

        if (isPublished) {
            await ttPage.waitForTimeout(2000);
            videoUrl = await ttPage.evaluate(() => {
                const a = document.querySelector('a[href*="/@"][href*="/video/"]');
                return a ? a.href : null;
            });
        }

        const result = {
            status: isPublished ? 'success' : 'processing',
            file: resolvedFile,
            caption: caption,
            current_url: currentUrl,
            video_url: videoUrl,
        };

        if (json) {
            console.log(JSON.stringify(result, null, 2));
        } else {
            console.log('\n====================================================');
            if (isPublished) {
                console.log('🎉 TIKTOK PUBLISHING SUCCESSFUL!');
                if (videoUrl) console.log(`🔗 Live Post URL: ${videoUrl}`);
            } else {
                console.log('ℹ️ Upload submitted and currently being processed by TikTok.');
            }
            console.log(`📍 Redirect URL: ${currentUrl}`);
            console.log('====================================================\n');
        }

        await browser.close();
        process.exit(0);
    } catch (err) {
        console.error('❌ TikTok Upload Error:', err.message);
        if (browser) await browser.close();
        process.exit(1);
    }
}

const args = parseArgs();
uploadToTikTok(args);
