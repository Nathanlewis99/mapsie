import { Config } from "@remotion/cli/config";

// Rendered in the cloud container with its pre-installed Chromium; locally Remotion uses its own.
if (process.env.REMOTION_CHROME) Config.setBrowserExecutable(process.env.REMOTION_CHROME);
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(92);
