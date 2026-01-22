----------------------------------------------------------------------------------
-- Company: 
-- Engineer: 
-- 
-- Create Date: 12/28/2025 10:22:51 PM
-- Design Name: 
-- Module Name: uart_tx - Behavioral
-- Project Name: 
-- Target Devices: 
-- Tool Versions: 
-- Description: 
-- 
-- Dependencies: 
-- 
-- Revision:
-- Revision 0.01 - File Created
-- Additional Comments:
-- 
----------------------------------------------------------------------------------


library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity uart_tx is
    Generic (
        CLK_PER_BIT : integer := 41666  -- 9600 bps @ 100MHz
    );
    Port (
        clk           : in  std_logic;
        tx_start      : in  std_logic;                     -- Pulso para empezar a enviar
        tx_data_in    : in  std_logic_vector(7 downto 0);  -- El byte a enviar
        tx_active     : out std_logic;                     -- '1' mientras está ocupado
        tx_serial_out : out std_logic;                     -- Salida física (Pin A18)
        tx_done       : out std_logic                      -- Pulso al terminar
    );
end uart_tx;

architecture Behavioral of uart_tx is
    type t_estado is (ST_IDLE, ST_START_BIT, ST_DATA_BITS, ST_STOP_BIT, ST_CLEANUP);
    signal estado_actual : t_estado := ST_IDLE;

    signal clk_count : integer range 0 to CLK_PER_BIT - 1 := 0;
    signal bit_index : integer range 0 to 7 := 0;
    signal tx_data   : std_logic_vector(7 downto 0) := (others => '0');
begin

    process(clk)
    begin
        if rising_edge(clk) then
            case estado_actual is

                when ST_IDLE =>
                    tx_active     <= '0';
                    tx_serial_out <= '1'; -- Reposo en '1'
                    tx_done       <= '0';
                    clk_count     <= 0;
                    bit_index     <= 0;

                    if tx_start = '1' then
                        tx_data       <= tx_data_in;
                        estado_actual <= ST_START_BIT;
                    end if;

                when ST_START_BIT =>
                    tx_active     <= '1';
                    tx_serial_out <= '0'; -- Bit de inicio
                    if clk_count < CLK_PER_BIT - 1 then
                        clk_count <= clk_count + 1;
                    else
                        clk_count <= 0;
                        estado_actual <= ST_DATA_BITS;
                    end if;

                when ST_DATA_BITS =>
                    tx_serial_out <= tx_data(bit_index);
                    if clk_count < CLK_PER_BIT - 1 then
                        clk_count <= clk_count + 1;
                    else
                        clk_count <= 0;
                        if bit_index < 7 then
                            bit_index <= bit_index + 1;
                        else
                            bit_index <= 0;
                            estado_actual <= ST_STOP_BIT;
                        end if;
                    end if;

                when ST_STOP_BIT =>
                    tx_serial_out <= '1'; -- Bit de parada
                    if clk_count < CLK_PER_BIT - 1 then
                        clk_count <= clk_count + 1;
                    else
                        tx_done       <= '1';
                        clk_count     <= 0;
                        estado_actual <= ST_CLEANUP;
                    end if;

                when ST_CLEANUP =>
                    tx_active     <= '0';
                    tx_done       <= '0';
                    estado_actual <= ST_IDLE;

            end case;
        end if;
    end process;
end Behavioral;
