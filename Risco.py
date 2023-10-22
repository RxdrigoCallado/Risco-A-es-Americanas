import yfinance as yf
import numpy as np
from scipy.stats import norm
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox

def calcular_metricas(ticker, start_date, end_date):
    try:
        # Obtendo os dados históricos do ticker
        dados = yf.download(ticker, start=start_date, end=end_date)

        # Calculando os retornos diários
        dados['Retorno'] = dados['Close'].pct_change()

        # Calculando o beta (opcional)
        benchmark_ticker = '^GSPC'  # Índice de referência (exemplo: S&P 500)
        benchmark_dados = yf.download(benchmark_ticker, start=start_date, end=end_date)
        benchmark_retorno = benchmark_dados['Close'].pct_change()
        cov = np.cov(dados['Retorno'].dropna(), benchmark_retorno.dropna())[0, 1]
        var = np.var(benchmark_retorno.dropna())
        beta = cov / var

        # Calculando o desvio padrão
        desvio_padrao = np.std(dados['Retorno'])

        # Filtrando apenas os retornos negativos
        retornos_negativos = dados['Retorno'][dados['Retorno'] < 0]

        # Calculando a volatilidade
        volatilidade = np.std(retornos_negativos)

        # Calculando o logaritmo da volatilidade
        log_volatilidade = np.log(volatilidade)

        return beta, desvio_padrao, volatilidade, log_volatilidade
    except Exception as e:
        return None

def calculate_var(returns, portfolio_value, confidence_level):
    expected_returns = returns.mean()
    volatility = returns[returns < 0].std()
    var = portfolio_value * (expected_returns - volatility * norm.ppf(1 - confidence_level))
    return var

# ...
def show_results():
    ticker = ticker_entry.get()
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    portfolio_value = float(portfolio_value_entry.get())

    if not ticker or not start_date or not end_date:
        messagebox.showerror("Erro", "Por favor, preencha todos os campos.")
        return

    try:
        start_date = datetime.strptime(start_date, "%d/%m/%Y")
        end_date = datetime.strptime(end_date, "%d/%m/%Y")
    except ValueError:
        messagebox.showerror("Erro", "As datas devem estar no formato DD/MM/AAAA.")
        return

    metricas = calcular_metricas(ticker, start_date, end_date)
    
    if metricas:
        beta, desvio_padrao, volatilidade, log_volatilidade = metricas
        returns = yf.download(ticker, start=start_date, end=end_date)['Adj Close'].pct_change().dropna()
        confidence_level = 0.95  # Define o nível de confiança
        var = calculate_var(returns, portfolio_value, confidence_level)

        # Calcula a porcentagem de perda máxima esperada
        var_percentage = (var / portfolio_value) * 100

        result_text.config(state="normal")
        result_text.delete("1.0", tk.END)
        result_text.insert(tk.END, f"Ticker: {ticker}\n")
        result_text.insert(tk.END, f"Beta: {beta:.2f}\n")
        result_text.insert(tk.END, f"Desvio Padrão: {desvio_padrao*100:.3f}\n")
        result_text.insert(tk.END, f"Volatilidade: {volatilidade*100:.3f}\n")
        result_text.insert(tk.END, f"Log da Volatilidade Negativa: {log_volatilidade:.2f}\n")
        result_text.insert(tk.END, f"Value at Risk (95% confidence): ${float(var):,.2f}\n")
        #result_text.insert(tk.END, f"Porcentagem de perda máxima esperada: {var_percentage:.2f}%\n")
        result_text.config(state="disabled")
    else:
        messagebox.showerror("Erro", f"Erro ao processar {ticker}. O ticker pode não estar disponível ou ocorreu outro erro.")


# Configuração da janela
window = tk.Tk()
window.title("Análise de Ações")
window.geometry("450x390")

# Rótulos e entradas de dados
tk.Label(window, text="Ticker da Ação:").pack()
ticker_entry = tk.Entry(window)
ticker_entry.pack()

tk.Label(window, text="Data de Início (DD/MM/AAAA):").pack()
start_date_entry = tk.Entry(window)
start_date_entry.pack()

tk.Label(window, text="Data de Fim (DD/MM/AAAA):").pack()
end_date_entry = tk.Entry(window)
end_date_entry.pack()

tk.Label(window, text="Valor do Portfólio:").pack()  # Adicione um rótulo para o valor do portfólio
portfolio_value_entry = tk.Entry(window)
portfolio_value_entry.pack()

# Botão para calcular métricas
calculate_button = tk.Button(window, text="Calcular Métricas", command=show_results)
calculate_button.pack()

# Texto para exibir resultados
result_text = tk.Text(window, height=10, width=50)
result_text.pack()
result_text.config(state="disabled")

# Iniciar a janela
window.mainloop()
