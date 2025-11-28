import { spawn } from 'child_process';
import path from 'path';
import fs from 'fs';

interface PipelineResult {
  success: boolean;
  output?: string;
  error?: string;
}

/**
 * Service to interact with the Python pipeline
 */
export class PipelineService {
  private pipelinePath: string;
  private pythonPath: string;

  constructor() {
    this.pipelinePath = process.env.PIPELINE_PATH || path.join(__dirname, '..', '..', '..', '..');
    this.pythonPath = process.env.PYTHON_PATH || 'python';
  }

  /**
   * Run the main pipeline for a specific dealer
   */
  async runPipeline(dealerId: string, options: {
    limit?: number;
    skipVideo?: boolean;
    skipImages?: boolean;
  } = {}): Promise<PipelineResult> {
    const args = ['run.py'];
    
    if (options.limit) args.push('--limit', options.limit.toString());
    if (options.skipVideo) args.push('--skip-video');
    if (options.skipImages) args.push('--skip-images');

    return this.runPythonScript(args);
  }

  /**
   * Process images for a listing
   */
  async processImages(inputDir: string, outputDir: string): Promise<PipelineResult> {
    const scriptPath = path.join('src', 'ai', 'image_processor_v2.py');
    return this.runPythonScript([scriptPath, inputDir, outputDir]);
  }

  /**
   * Generate script for a listing
   */
  async generateScript(listingData: Record<string, unknown>): Promise<PipelineResult> {
    // Create temp file with listing data
    const tempFile = path.join(this.pipelinePath, 'temp_listing.json');
    fs.writeFileSync(tempFile, JSON.stringify(listingData));
    
    try {
      const result = await this.runPythonScript([
        '-c',
        `
import json
from src.ai.script_generator import ScriptGenerator

with open('${tempFile.replace(/\\/g, '\\\\')}', 'r') as f:
    data = json.load(f)

gen = ScriptGenerator(provider='openai')
script = gen.generate_script(
    year=data['year'],
    make=data['make'],
    model=data['model'],
    price=data['price'],
    condition=data.get('condition', 'Used'),
    odometer=data.get('odometer'),
    color=data.get('color'),
    features=data.get('features', [])
)
print(script)
        `
      ]);
      return result;
    } finally {
      if (fs.existsSync(tempFile)) {
        fs.unlinkSync(tempFile);
      }
    }
  }

  /**
   * Generate voiceover for a script
   */
  async generateVoiceover(scriptPath: string, outputPath: string): Promise<PipelineResult> {
    return this.runPythonScript([
      '-c',
      `
from src.ai.voice_generator import VoiceGenerator

gen = VoiceGenerator(provider='gtts')
success = gen.generate_from_script_file('${scriptPath.replace(/\\/g, '\\\\')}', '${outputPath.replace(/\\/g, '\\\\')}')
print('SUCCESS' if success else 'FAILED')
      `
    ]);
  }

  /**
   * Generate video for a listing
   */
  async generateVideo(listingId: string, dealerId: string): Promise<PipelineResult> {
    return this.runPythonScript([
      '-c',
      `
from src.video.video_composer import VideoComposer
from src.data.asset_manager import AssetManager

# This would need proper implementation based on your pipeline
print('Video generation triggered for ${listingId}')
      `
    ]);
  }

  /**
   * Generate QR code
   */
  async generateQRCode(url: string, outputPath: string): Promise<PipelineResult> {
    return this.runPythonScript([
      '-c',
      `
from src.ai.qr_generator import QRGenerator

gen = QRGenerator()
gen.generate('${url}', '${outputPath.replace(/\\/g, '\\\\')}')
print('QR code generated')
      `
    ]);
  }

  /**
   * Run a Python script
   */
  private runPythonScript(args: string[]): Promise<PipelineResult> {
    return new Promise((resolve) => {
      const process = spawn(this.pythonPath, args, {
        cwd: this.pipelinePath,
        env: { ...process.env }
      });

      let stdout = '';
      let stderr = '';

      process.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      process.on('close', (code) => {
        if (code === 0) {
          resolve({ success: true, output: stdout.trim() });
        } else {
          resolve({ success: false, error: stderr || stdout });
        }
      });

      process.on('error', (err) => {
        resolve({ success: false, error: err.message });
      });
    });
  }
}

export const pipelineService = new PipelineService();

