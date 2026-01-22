library IEEE;
use IEEE.STD_LOGIC_1164.ALL;

-- Uncomment the following library declaration if using
-- arithmetic functions with Signed or Unsigned values
--use IEEE.NUMERIC_STD.ALL;

-- Uncomment the following library declaration if instantiating
-- any Xilinx leaf cells in this code.
--library UNISIM;
--use UNISIM.VComponents.all;

entity top_sistema is
    Port (
        clk_hw      : in  std_logic;
        reset_hw    : in  std_logic;
        rx_laser    : in  std_logic; -- Entrada desde el fototransistor
        tx_to_pc    : out std_logic  -- Salida al pin A18
    );
end top_sistema;

architecture Behavioral of top_sistema is
    signal data_bus : std_logic_vector(7 downto 0);
    signal ready_pulse : std_logic;
begin
    -- Instancia del Receptor 
    RX_INST: entity work.modulo_uart
        port map (
            clk      => clk_hw,
            reset    => reset_hw,
            rx_input => rx_laser,
            data_out => data_bus,
            rx_ready => ready_pulse
        );

    -- Instancia del Transmisor
    TX_INST: entity work.uart_tx
        port map (
            clk           => clk_hw,
            tx_start      => ready_pulse, -- Se activa cuando el RX termina
            tx_data_in    => data_bus,
            tx_serial_out => tx_to_pc
        );
end Behavioral;
