import amqp from 'amqplib';
import puppeteer from 'puppeteer';

async function captureScreenshot(url: string): Promise<Buffer> {
    const browser = await puppeteer.launch();
    const page = await browser.newPage();
    try {
        await page.setDefaultNavigationTimeout(60000); // Increase timeout to 60 seconds
        console.log(`Navigating to ${url}`);
        await page.goto(url, { waitUntil: 'networkidle0' });
        console.log(`Successfully loaded ${url}`);
        const screenshot = await page.screenshot({ fullPage: true });
        console.log(`Screenshot captured for ${url}`);
        return screenshot;
    } catch (error) {
        console.error(`Error capturing screenshot for ${url}:`, error);
        throw error;
    } finally {
        await browser.close();
    }
}

async function processUrls() {
    const connection = await amqp.connect('amqp://localhost');
    const channel = await connection.createChannel();

    await channel.assertQueue('url_queue', { durable: true });
    await channel.assertQueue('screenshot_queue', { durable: false });

    console.log(" [*] Waiting for URLs. To exit press CTRL+C");

    channel.prefetch(1);
    await channel.consume('url_queue', async (msg) => {
        if (msg !== null) {
            const urlData = JSON.parse(msg.content.toString());
            console.log(" [x] Received URL:", urlData.url);

            try {
                const screenshot = await captureScreenshot(urlData.url);
                
                await channel.sendToQueue('screenshot_queue', screenshot, {
                    headers: { url: urlData.url }
                });

                console.log(` [x] Screenshot taken and sent to queue for ${urlData.url}`);
                channel.ack(msg);
            } catch (error) {
                console.error(`Error processing URL ${urlData.url}:`, error);
                // Implement retry logic or move to a dead-letter queue
                if (msg.fields.redelivered) {
                    console.log(`Message for ${urlData.url} has been redelivered, moving to dead-letter queue`);
                    // Implement dead-letter queue logic here
                    channel.ack(msg);
                } else {
                    console.log(`Requeueing message for ${urlData.url}`);
                    channel.nack(msg, false, true);
                }
            }
        }
    }, { noAck: false });
}

processUrls().catch(console.error);