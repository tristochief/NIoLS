/**
 * Testbench for Laser Driver Circuit
 * 
 * Tests the laser driver with pulse modulation and safety interlock.
 * Simulates GPIO control, PWM generation, and interlock monitoring.
 */

`timescale 1ns / 1ps

module laser_driver_tb;

    // Test signals
    reg clk;
    reg reset;
    reg enable;
    reg interlock_safe;
    reg [7:0] pwm_duty_cycle;
    reg pulse_enable;
    reg [31:0] pulse_duration;  // in clock cycles
    
    wire laser_output;
    wire interlock_status;
    wire pwm_output;
    
    // Instantiate DUT
    laser_driver dut (
        .clk(clk),
        .reset(reset),
        .enable(enable),
        .interlock_safe(interlock_safe),
        .pwm_duty_cycle(pwm_duty_cycle),
        .pulse_enable(pulse_enable),
        .pulse_duration(pulse_duration),
        .laser_output(laser_output),
        .interlock_status(interlock_status),
        .pwm_output(pwm_output)
    );
    
    // Clock generation (1 MHz = 1 μs period)
    initial begin
        clk = 0;
        forever #500 clk = ~clk;
    end
    
    // Test stimulus
    initial begin
        $display("=== Laser Driver Testbench ===");
        $display("Time\tEnable\tInterlock\tLaser\tPWM");
        $display("----------------------------------------");
        
        // Initialize
        reset = 1;
        enable = 0;
        interlock_safe = 0;
        pwm_duty_cycle = 0;
        pulse_enable = 0;
        pulse_duration = 0;
        #1000;
        
        reset = 0;
        #1000;
        
        // Test 1: Interlock unsafe - laser should not enable
        $display("\nTest 1: Interlock Unsafe");
        interlock_safe = 0;
        enable = 1;
        #10000;
        $display("%0t\t%0d\t%0d\t\t%0d\t%0d", $time, enable, interlock_safe, laser_output, pwm_output);
        
        // Test 2: Interlock safe - laser should enable
        $display("\nTest 2: Interlock Safe - Enable Laser");
        interlock_safe = 1;
        #1000;
        enable = 1;
        #10000;
        $display("%0t\t%0d\t%0d\t\t%0d\t%0d", $time, enable, interlock_safe, laser_output, pwm_output);
        
        // Test 3: Disable laser
        $display("\nTest 3: Disable Laser");
        enable = 0;
        #10000;
        $display("%0t\t%0d\t%0d\t\t%0d\t%0d", $time, enable, interlock_safe, laser_output, pwm_output);
        
        // Test 4: PWM at 50% duty cycle
        $display("\nTest 4: PWM 50%% Duty Cycle");
        enable = 1;
        pwm_duty_cycle = 128;  // 50%
        #100000;  // Observe PWM
        $display("%0t\t%0d\t%0d\t\t%0d\t%0d", $time, enable, interlock_safe, laser_output, pwm_output);
        
        // Test 5: PWM at 25% duty cycle
        $display("\nTest 5: PWM 25%% Duty Cycle");
        pwm_duty_cycle = 64;  // 25%
        #100000;
        $display("%0t\t%0d\t%0d\t\t%0d\t%0d", $time, enable, interlock_safe, laser_output, pwm_output);
        
        // Test 6: Single pulse
        $display("\nTest 6: Single Pulse");
        enable = 0;
        pwm_duty_cycle = 0;
        pulse_duration = 1000;  // 1000 clock cycles = 1 ms
        pulse_enable = 1;
        #2000;
        pulse_enable = 0;
        #5000;
        $display("%0t\t%0d\t%0d\t\t%0d\t%0d", $time, enable, interlock_safe, laser_output, pwm_output);
        
        // Test 7: Interlock failure during operation
        $display("\nTest 7: Interlock Failure During Operation");
        enable = 1;
        interlock_safe = 1;
        #10000;
        interlock_safe = 0;  // Interlock opens
        #1000;
        $display("%0t\t%0d\t%0d\t\t%0d\t%0d", $time, enable, interlock_safe, laser_output, pwm_output);
        // Laser should disable immediately
        
        // Test 8: Emergency stop
        $display("\nTest 8: Emergency Stop");
        interlock_safe = 1;
        enable = 1;
        #10000;
        reset = 1;  // Emergency stop
        #1000;
        $display("%0t\t%0d\t%0d\t\t%0d\t%0d", $time, enable, interlock_safe, laser_output, pwm_output);
        reset = 0;
        
        // Test 9: PWM frequency test
        $display("\nTest 9: PWM Frequency Test");
        enable = 1;
        pwm_duty_cycle = 128;  // 50%
        #1000000;  // Observe PWM over time
        
        $display("\n=== Test Complete ===");
        #10000;
        $finish;
    end
    
    // Monitor outputs
    always @(posedge clk) begin
        // Check that laser doesn't turn on without interlock
        if (laser_output && !interlock_safe) begin
            $display("ERROR: Laser on without interlock at time %0t", $time);
        end
        
        // Check interlock status
        if (interlock_status != interlock_safe) begin
            $display("WARNING: Interlock status mismatch at time %0t", $time);
        end
    end

endmodule

/**
 * Laser Driver Module (DUT)
 * Implements laser control with PWM and safety interlock
 */
module laser_driver(
    input clk,
    input reset,
    input enable,
    input interlock_safe,
    input [7:0] pwm_duty_cycle,
    input pulse_enable,
    input [31:0] pulse_duration,
    output reg laser_output,
    output interlock_status,
    output pwm_output
);
    
    // Interlock status
    assign interlock_status = interlock_safe;
    
    // PWM counter
    reg [7:0] pwm_counter;
    
    always @(posedge clk) begin
        if (reset) begin
            pwm_counter <= 0;
            laser_output <= 0;
        end else begin
            pwm_counter <= pwm_counter + 1;
            
            // PWM generation
            if (enable && interlock_safe) begin
                if (pwm_duty_cycle == 255) begin
                    // 100% duty cycle = continuous
                    laser_output <= 1;
                end else if (pwm_duty_cycle == 0) begin
                    laser_output <= 0;
                end else begin
                    laser_output <= (pwm_counter < pwm_duty_cycle);
                end
            end else begin
                laser_output <= 0;
            end
        end
    end
    
    // Pulse generation
    reg [31:0] pulse_counter;
    reg pulse_active;
    
    always @(posedge clk) begin
        if (reset) begin
            pulse_counter <= 0;
            pulse_active <= 0;
        end else if (pulse_enable && !pulse_active) begin
            pulse_active <= 1;
            pulse_counter <= 0;
        end else if (pulse_active) begin
            if (pulse_counter < pulse_duration) begin
                pulse_counter <= pulse_counter + 1;
                if (interlock_safe) begin
                    laser_output <= 1;
                end
            end else begin
                pulse_active <= 0;
                laser_output <= 0;
            end
        end
    end
    
    // PWM output (for monitoring)
    assign pwm_output = laser_output;

endmodule

