/*
 * WebP Decoder MicroPython Module for RP2350
 * Complete implementation with libwebp integration
 * 
 * This version integrates the actual libwebp library.
 * To use this, you need to:
 * 1. Download libwebp source
 * 2. Update micropython.mk to include libwebp sources
 * 3. Replace webpdec.c with this file (rename to webpdec.c)
 */

#include "py/runtime.h"
#include "py/obj.h"
#include "py/objstr.h"

// Uncomment when libwebp is integrated
// #include "webp/decode.h"

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
    
    // Get expected dimensions
    mp_int_t expected_width = mp_obj_get_int(width_obj);
    mp_int_t expected_height = mp_obj_get_int(height_obj);
    
    // Validate dimensions
    if (expected_width <= 0 || expected_width > 256 || 
        expected_height <= 0 || expected_height > 256) {
        mp_raise_ValueError(MP_ERROR_TEXT("Invalid dimensions"));
    }
    
    /* 
     * LIBWEBP INTEGRATION CODE (uncomment when libwebp is available)
     * 
    int width, height;
    
    // Decode WebP to RGB
    uint8_t* rgb_data = WebPDecodeRGB(
        (const uint8_t*)bufinfo.buf, 
        bufinfo.len, 
        &width, 
        &height
    );
    
    if (rgb_data == NULL) {
        mp_raise_ValueError(MP_ERROR_TEXT("WebP decode failed"));
    }
    
    // Verify dimensions match
    if (width != expected_width || height != expected_height) {
        WebPFree(rgb_data);
        mp_raise_ValueError(MP_ERROR_TEXT("Image dimensions don't match"));
    }
    
    // Allocate RGB565 output buffer
    size_t output_size = width * height * 2;
    byte *output = m_new(byte, output_size);
    
    if (output == NULL) {
        WebPFree(rgb_data);
        mp_raise_msg(&mp_type_MemoryError, MP_ERROR_TEXT("Cannot allocate output buffer"));
    }
    
    // Convert RGB888 to RGB565
    for (int i = 0; i < width * height; i++) {
        uint8_t r = rgb_data[i * 3 + 0];
        uint8_t g = rgb_data[i * 3 + 1];
        uint8_t b = rgb_data[i * 3 + 2];
        
        // Pack into RGB565: RRRRR GGGGGG BBBBB
        uint16_t rgb565 = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3);
        
        // Store as little-endian
        output[i * 2 + 0] = rgb565 & 0xFF;
        output[i * 2 + 1] = (rgb565 >> 8) & 0xFF;
    }
    
    // Free WebP decode buffer
    WebPFree(rgb_data);
    
    // Create and return bytearray
    return mp_obj_new_bytearray_by_ref(output_size, output);
    */
    
    // Placeholder: return error until libwebp is integrated
    mp_raise_NotImplementedError(
        MP_ERROR_TEXT("libwebp not yet integrated - use webpdec.c placeholder version")
    );
}
STATIC MP_DEFINE_CONST_FUN_OBJ_3(webpdec_decode_obj, webpdec_decode);

// Module version info
STATIC mp_obj_t webpdec_version(void) {
    return mp_obj_new_str("0.1.0-libwebp", 14);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(webpdec_version_obj, webpdec_version);

// Module globals table
STATIC const mp_rom_map_elem_t webpdec_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_webpdec) },
    { MP_ROM_QSTR(MP_QSTR_decode), MP_ROM_PTR(&webpdec_decode_obj) },
    { MP_ROM_QSTR(MP_QSTR_version), MP_ROM_PTR(&webpdec_version_obj) },
};
STATIC MP_DEFINE_CONST_DICT(webpdec_module_globals, webpdec_module_globals_table);

// Module definition
const mp_obj_module_t webpdec_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t *)&webpdec_module_globals,
};

// Register module
MP_REGISTER_MODULE(MP_QSTR_webpdec, webpdec_module);
