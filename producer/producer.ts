import puppeteer from 'puppeteer';
import amqp from 'amqplib';

async function captureScreenshot(url: string): Promise<Buffer> {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    await page.goto(url, { waitUntil: 'networkidle0' });
    const screenshot = await page.screenshot({ fullPage: true });
    await browser.close();
    return screenshot;
}

async function sendScreenshotToQueue(screenshot: Buffer, url: string) {
    try {
        const connection = await amqp.connect('amqp://localhost');
        const channel = await connection.createChannel();
        const queue = 'screenshot_queue';

        await channel.assertQueue(queue, { durable: false });
        channel.sendToQueue(queue, screenshot, {
            persistent: true,
            headers: { url: url }
        });

        console.log(`Screenshot of ${url} sent to queue`);
        await channel.close();
        await connection.close();
    } catch (error) {
        console.error('Error sending screenshot to queue:', error);
    }
}

async function main() {
    const url = 'https://www.ai-synapse.io';  
    const screenshot = await captureScreenshot(url);
    await sendScreenshotToQueue(screenshot, url);
}

main().catch(console.error);