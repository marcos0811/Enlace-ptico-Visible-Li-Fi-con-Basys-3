    
 library IEEE;
use IEEE.STD_LOGIC_1164.ALL;
  
entity transmisor is
        Port (
            clk        : in  STD_LOGIC;  -- reloj del sistema
            rx      : in  STD_LOGIC;  -- uart
            laser_out : out STD_LOGIC   -- señal modulada OOK
        );   
end transmisor;
    
architecture Behavioral of transmisor is
    
        signal dato_rx_s     : STD_LOGIC_VECTOR(7 downto 0);
        signal dato_valido_s : STD_LOGIC;
        signal bit_tx_s      : STD_LOGIC;
        signal ocupado_s     : STD_LOGIC;
    
begin
    
        -- ======================
        -- UART RX
        -- ======================
        uart_rx_inst : entity work.uart_rx
            port map (
                clk         => clk,
                rx          => rx,
                dato_rx     => dato_rx_s,
                dato_valido => dato_valido_s
            );
    
        -- ======================
        -- CODIFICADOR
        -- ======================
        codificador_inst : entity work.codificador
            port map (
                clk          => clk,
                dato_entrada => dato_rx_s,
                dato_valido  => dato_valido_s,
                bit_tx       => bit_tx_s,
                ocupado      => ocupado_s
            );
    
        -- ======================
        -- MODULADOR OOK
        -- ======================
        modulador_inst : entity work.modulador
            port map (
                clk        => clk,
                bit_tx     => bit_tx_s,
                laser_out  => laser_out
            );
    
end Behavioral;   
