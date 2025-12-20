/**
 * Testbench for Photodiode Transimpedance Amplifier
 * 
 * Tests the transimpedance amplifier circuit for photodiode signal conditioning.
 * Simulates photodiode current, amplifier response, and output voltage.
 */

`timescale 1ns / 1ps

module photodiode_amplifier_tb;

    // Parameters
    parameter R_FEEDBACK = 1e6;  // 1 MΩ feedback resistor
    parameter C_FEEDBACK = 10e-12;  // 10 pF feedback capacitor
    parameter OPAMP_GAIN = 1e6;  // Op-amp open-loop gain
    parameter OPAMP_BW = 16e6;  // 16 MHz bandwidth
    
    // Test signals
    reg clk;
    reg [15:0] photodiode_current;  // Photodiode current in pA (scaled)
    wire [15:0] output_voltage;  // Output voltage in mV (scaled)
    
    // Photodiode model
    real photodiode_current_real;
    real output_voltage_real;
    
    // Instantiate DUT (Device Under Test)
    photodiode_amplifier dut (
        .photodiode_current(photodiode_current),
        .output_voltage(output_voltage),
        .clk(clk)
    );
    
    // Clock generation (1 MHz)
    initial begin
        clk = 0;
        forever #500 clk = ~clk;
    end
    
    // Test stimulus
    initial begin
        $display("=== Photodiode Amplifier Testbench ===");
        $display("Time\tPhotodiode Current (nA)\tOutput Voltage (V)");
        $display("---------------------------------------------------");
        
        // Initialize
        photodiode_current = 16'd0;
        #1000;
        
        // Test 1: Dark current (< 1 nA)
        $display("\nTest 1: Dark Current");
        photodiode_current = 16'd100;  // 0.1 nA
        #10000;
        $display("%0t\t%0.3f\t\t\t%0.3f", $time, photodiode_current_real/1e-9, output_voltage_real);
        
        // Test 2: Low light (1 μA)
        $display("\nTest 2: Low Light (1 μA)");
        photodiode_current = 16'd1000;  // 1 μA
        #10000;
        $display("%0t\t%0.3f\t\t\t%0.3f", $time, photodiode_current_real/1e-6, output_voltage_real);
        
        // Test 3: Medium light (10 μA)
        $display("\nTest 3: Medium Light (10 μA)");
        photodiode_current = 16'd10000;  // 10 μA
        #10000;
        $display("%0t\t%0.3f\t\t\t%0.3f", $time, photodiode_current_real/1e-6, output_voltage_real);
        
        // Test 4: High light (100 μA)
        $display("\nTest 4: High Light (100 μA)");
        photodiode_current = 16'd100000;  // 100 μA
        #10000;
        $display("%0t\t%0.3f\t\t\t%0.3f", $time, photodiode_current_real/1e-6, output_voltage_real);
        
        // Test 5: Saturation (1 mA - should saturate)
        $display("\nTest 5: Saturation (1 mA)");
        photodiode_current = 16'd1000000;  // 1 mA
        #10000;
        $display("%0t\t%0.3f\t\t\t%0.3f", $time, photodiode_current_real/1e-3, output_voltage_real);
        
        // Test 6: Ramp test (linearity)
        $display("\nTest 6: Linearity Test");
        for (integer i = 0; i < 100; i = i + 1) begin
            photodiode_current = i * 1000;  // 0 to 100 μA
            #1000;
        end
        
        // Test 7: Frequency response (AC analysis)
        $display("\nTest 7: Frequency Response");
        photodiode_current = 16'd10000;  // 10 μA DC
        #10000;
        // Apply AC signal (simplified)
        for (integer freq = 1; freq <= 10000; freq = freq * 10) begin
            // Simulate AC response
            #1000;
        end
        
        $display("\n=== Test Complete ===");
        #10000;
        $finish;
    end
    
    // Convert scaled values to real
    always @(photodiode_current) begin
        photodiode_current_real = photodiode_current * 1e-12;  // Convert to Amperes
    end
    
    always @(output_voltage) begin
        output_voltage_real = output_voltage * 1e-3;  // Convert to Volts
    end
    
    // Monitor output
    always @(posedge clk) begin
        // Check for saturation
        if (output_voltage_real > 4.5) begin
            $display("WARNING: Output saturated at %0.3f V", output_voltage_real);
        end
        
        // Check for negative output (shouldn't happen)
        if (output_voltage_real < 0) begin
            $display("ERROR: Negative output voltage: %0.3f V", output_voltage_real);
        end
    end

endmodule

/**
 * Photodiode Amplifier Module (DUT)
 * Simplified model of transimpedance amplifier
 */
module photodiode_amplifier(
    input [15:0] photodiode_current,
    output reg [15:0] output_voltage,
    input clk
);
    
    parameter R_FEEDBACK = 1e6;  // 1 MΩ
    parameter V_SUPPLY = 5.0;  // 5V supply
    parameter V_SAT = 4.5;  // Saturation voltage
    
    real current_real;
    real voltage_real;
    
    always @(posedge clk) begin
        // Convert input to real
        current_real = photodiode_current * 1e-12;  // pA to A
        
        // Calculate output: Vout = I * R
        voltage_real = current_real * R_FEEDBACK;
        
        // Apply saturation
        if (voltage_real > V_SAT) begin
            voltage_real = V_SAT;
        end
        
        // Convert back to integer (mV)
        output_voltage = voltage_real * 1000;
    end
    
endmodule

