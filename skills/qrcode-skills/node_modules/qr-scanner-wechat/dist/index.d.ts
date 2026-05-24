interface ScanResult {
    text: string | null;
    rect?: {
        x: number;
        y: number;
        width: number;
        height: number;
    };
    rectCanvas?: HTMLCanvasElement;
}
interface ScanOptions {
    /**
     * Include the canvas of the detected QR code.
     *
     * Currently only works on browsers.
     * @default false
     */
    includeRectCanvas?: boolean;
}
interface ImageDataLike {
    data: Uint8ClampedArray;
    width: number;
    height: number;
}
type ImageSource = ImageDataLike | ImageData | HTMLCanvasElement | HTMLImageElement;
declare function ready(): Promise<void>;
declare function scan(input: ImageSource, options?: ScanOptions): Promise<ScanResult>;

export { ImageDataLike, ImageSource, ScanOptions, ScanResult, ready, scan };
