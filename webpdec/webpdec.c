/*
 * WebP Decoder MicroPython Module for RP2350
 * Decodes WebP images to RGB565 format for HUB75 displays
 */

#include "py/runtime.h"
#include "py/obj.h"
#include "py/objstr.h"

// We'll use a minimal WebP decoder implementation
// For production, you'd use libwebp, but we'll create a simple wrapper here

// Function prototypes
STATIC mp_obj_t webpdec_decode(mp_obj_t data_obj, mp_obj_t width_obj, mp_obj_t height_obj);

/*
 * Decode WebP image to RGB565
 * 
 * Args:
 *   data: bytes - WebP image data
 *   width: int - Expected width
 *   height: int - Expected height
 * 
 * Returns:
 *   bytearray - RGB565 pixel data (width * height * 2 bytes)
 */
STATIC mp_obj_t webpdec_decode(mp_obj_t data_obj, mp_obj_t width_obj, mp_obj_t height_obj) {
    // Get WebP data
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(data_obj, &bufinfo, MP_BUFFER_READ);
    
    // Get dimensions
    mp_int_t width = mp_obj_get_int(width_obj);
    mp_int_t height = mp_obj_get_int(height_obj);
    
    // Validate dimensions
    if (width <= 0 || width > 256 || height <= 0 || height > 256) {
        mp_raise_ValueError(MP_ERROR_TEXT("Invalid dimensions"));
    }
    
    // Calculate output size (RGB565 = 2 bytes per pixel)
    size_t output_size = width * height * 2;
    
    // Allocate output buffer
    byte *output = m_new(byte, output_size);
    if (output == NULL) {
        mp_raise_msg(&mp_type_MemoryError, MP_ERROR_TEXT("Cannot allocate decode buffer"));
    }
    
    /*
     * IMPORTANT: This is a placeholder implementation!
     * 
     * In a real implementation, you would:
     * 1. Use libwebp's WebPDecodeRGB() or similar
     * 2. Convert RGB888 to RGB565 if needed
     * 
     * Example with libwebp (pseudo-code):
     * 
     * #include "webp/decode.h"
     * 
     * int img_width, img_height;
     * uint8_t* rgb_data = WebPDecodeRGB(bufinfo.buf, bufinfo.len, &img_width, &img_height);
     * 
     * if (rgb_data == NULL) {
     *     mp_raise_ValueError(MP_ERROR_TEXT("WebP decode failed"));
     * }
     * 
     * // Convert RGB888 to RGB565
     * for (int i = 0; i < width * height; i++) {
     *     uint8_t r = rgb_data[i * 3 + 0];
     *     uint8_t g = rgb_data[i * 3 + 1];
     *     uint8_t b = rgb_data[i * 3 + 2];
     *     
     *     uint16_t rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3);
     *     
     *     output[i * 2 + 0] = rgb565 & 0xFF;         // Low byte
     *     output[i * 2 + 1] = (rgb565 >> 8) & 0xFF;  // High byte
     * }
     * 
     * WebPFree(rgb_data);
     */
    
    // For now, create a test pattern (red/green gradient)
    // This allows testing without WebP library
    for (int y = 0; y < height; y++) {
        for (int x = 0; x < width; x++) {
            int idx = (y * width + x) * 2;
            
            // Create a simple gradient test pattern
            uint8_t r = (x * 255) / width;
            uint8_t g = (y * 255) / height;
            uint8_t b = 128;
            
            // Convert RGB888 to RGB565
            uint16_t rgb565 = ((r >> 3) << 11) | ((g >> 2) << 5) | (b >> 3);
            
            output[idx + 0] = rgb565 & 0xFF;
            output[idx + 1] = (rgb565 >> 8) & 0xFF;
        }
    }
    
    // Create bytearray object
    mp_obj_t result = mp_obj_new_bytearray_by_ref(output_size, output);
    
    return result;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(webpdec_decode_obj, webpdec_decode);

// Module globals table
STATIC const mp_rom_map_elem_t webpdec_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_webpdec) },
    { MP_ROM_QSTR(MP_QSTR_decode), MP_ROM_PTR(&webpdec_decode_obj) },
};
STATIC MP_DEFINE_CONST_DICT(webpdec_module_globals, webpdec_module_globals_table);

// Module definition
const mp_obj_module_t webpdec_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&webpdec_module_globals,
};

// Register module
MP_REGISTER_MODULE(MP_QSTR_webpdec, webpdec_module);
