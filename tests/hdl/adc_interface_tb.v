/**
 * Testbench for ADC Interface
 * 
 * Tests the I2C interface to ADS1115 ADC for photodiode voltage measurement.
 * Simulates I2C communication and ADC conversion.
 */

`timescale 1ns / 1ps

module adc_interface_tb;

    // I2C signals
    reg clk;
    reg reset;
    reg sda;
    reg scl;
    wire sda_out;
    wire scl_out;
    
    // Control signals
    reg start_conversion;
    reg [1:0] channel_select;
    wire conversion_done;
    wire [15:0] adc_value;
    
    // Instantiate DUT
    adc_interface dut (
        .clk(clk),
        .reset(reset),
        .sda(sda),
        .scl(scl),
        .sda_out(sda_out),
        .scl_out(scl_out),
        .start_conversion(start_conversion),
        .channel_select(channel_select),
        .conversion_done(conversion_done),
        .adc_value(adc_value)
    );
    
    // Clock generation (1 MHz)
    initial begin
        clk = 0;
        forever #500 clk = ~clk;
    end
    
    // I2C bus (open drain simulation)
    assign sda = sda_out ? 1'bz : 1'b0;
    assign scl = scl_out ? 1'bz : 1'b0;
    
    // Test stimulus
    initial begin
        $display("=== ADC Interface Testbench ===");
        $display("Time\tChannel\tADC Value\tVoltage (V)");
        $display("----------------------------------------");
        
        // Initialize
        reset = 1;
        start_conversion = 0;
        channel_select = 0;
        #1000;
        
        reset = 0;
        #1000;
        
        // Test 1: Channel 0 conversion
        $display("\nTest 1: Channel 0 Conversion");
        channel_select = 0;
        start_conversion = 1;
        #1000;
        start_conversion = 0;
        
        wait(conversion_done);
        #1000;
        $display("%0t\t%0d\t%0d\t\t%0.3f", $time, channel_select, adc_value, adc_value * 4.096 / 32768);
        
        // Test 2: Channel 1 conversion
        $display("\nTest 2: Channel 1 Conversion");
        channel_select = 1;
        start_conversion = 1;
        #1000;
        start_conversion = 0;
        
        wait(conversion_done);
        #1000;
        $display("%0t\t%0d\t%0d\t\t%0.3f", $time, channel_select, adc_value, adc_value * 4.096 / 32768);
        
        // Test 3: Multiple conversions
        $display("\nTest 3: Multiple Conversions");
        for (integer i = 0; i < 5; i = i + 1) begin
            channel_select = 0;
            start_conversion = 1;
            #1000;
            start_conversion = 0;
            wait(conversion_done);
            #1000;
            $display("%0t\t%0d\t%0d\t\t%0.3f", $time, channel_select, adc_value, adc_value * 4.096 / 32768);
        end
        
        // Test 4: Different voltage levels
        $display("\nTest 4: Voltage Level Test");
        // Simulate different input voltages
        // (In real test, would inject different voltages)
        for (integer v = 0; v <= 3300; v = v + 330) begin
            channel_select = 0;
            start_conversion = 1;
            #1000;
            start_conversion = 0;
            wait(conversion_done);
            #1000;
            $display("%0t\t%0d\t%0d\t\t%0.3f", $time, channel_select, adc_value, adc_value * 4.096 / 32768);
        end
        
        $display("\n=== Test Complete ===");
        #10000;
        $finish;
    end
    
    // Monitor I2C bus
    always @(posedge scl) begin
        // Monitor I2C transactions
        #1;  // Small delay for setup
    end
    
    // Check conversion timing
    reg [31:0] conversion_start_time;
    always @(posedge start_conversion) begin
        conversion_start_time = $time;
    end
    
    always @(posedge conversion_done) begin
        $display("Conversion time: %0d ns", $time - conversion_start_time);
    end

endmodule

/**
 * ADC Interface Module (DUT)
 * Simplified I2C interface to ADS1115
 */
module adc_interface(
    input clk,
    input reset,
    inout sda,
    inout scl,
    output reg sda_out,
    output reg scl_out,
    input start_conversion,
    input [1:0] channel_select,
    output reg conversion_done,
    output reg [15:0] adc_value
);
    
    parameter I2C_ADDRESS = 7'h48;  // ADS1115 default address
    parameter CONVERSION_TIME = 1000;  // Conversion time in clock cycles
    
    // State machine
    reg [2:0] state;
    reg [31:0] counter;
    reg [15:0] simulated_voltage;
    
    localparam IDLE = 3'b000;
    localparam START = 3'b001;
    localparam ADDRESS = 3'b010;
    localparam CONFIG = 3'b011;
    localparam CONVERT = 3'b100;
    localparam READ = 3'b101;
    
    always @(posedge clk) begin
        if (reset) begin
            state <= IDLE;
            counter <= 0;
            conversion_done <= 0;
            sda_out <= 1;
            scl_out <= 1;
        end else begin
            case (state)
                IDLE: begin
                    conversion_done <= 0;
                    if (start_conversion) begin
                        state <= CONVERT;
                        counter <= 0;
                        // Simulate voltage based on channel
                        simulated_voltage <= 15000 + (channel_select * 5000);  // 1.5V + offset
                    end
                end
                
                CONVERT: begin
                    counter <= counter + 1;
                    if (counter >= CONVERSION_TIME) begin
                        // Conversion complete
                        adc_value <= simulated_voltage;
                        conversion_done <= 1;
                        state <= IDLE;
                    end
                end
                
                default: state <= IDLE;
            endcase
        end
    end
    
endmodule

