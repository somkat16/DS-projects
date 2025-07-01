import streamlit as st
import yfinance as yf
import datetime
import os
from openai import AzureOpenAI

### OPEN AI ####
endpoint = "https://somka-mci3w7ew-eastus2.cognitiveservices.azure.com/"
model_name = "gpt-35-turbo"
deployment = "stockchat"

subscription_key = "AgH6hWmmiRQ1OCxoWcQBa8NyDm1CvgqgchNR92YVlusOZtx5wKbrJQQJ99BFACHYHv6XJ3w3AAAAACOGziOF"
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)


### STREAMLIT UI ###

st.title("Stock AI Assistant")
st.write("Enter a stock ticker to fetch current and historical price data.")

# Input from user
ticker_symbol = st.text_input("Enter Stock Ticker (e.g., AAPL, MSFT, TSLA):", "AAPL").strip().upper()

# Select date range
start_date = st.date_input("Start Date", datetime.date(2024, 1, 1))
end_date = st.date_input("End Date", datetime.date.today())

# Validate date range
if start_date >= end_date:
    st.error("Start date must be before end date.")
else:
    if st.button("Fetch Stock Data"):
        try:
            st.info(f"Fetching data for `{ticker_symbol}` from {start_date} to {end_date}...")

            # Fetch the stock data
            stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)

            if stock_data.empty:
                st.warning(" No data found. Please check the ticker and date range.")
                st.text(f"Debug: Ticker = {repr(ticker_symbol)}")
            else:
                st.success(f" Showing data for {ticker_symbol}")
                st.dataframe(stock_data.tail())
                st.line_chart(stock_data["Close"])
        except Exception as e:
            st.error(f"Error fetching data: {e}")


### AI EXPLANATION/PROMPT ENGINEERING ### 
stock_data = yf.download(ticker_symbol, start=start_date, end=end_date)

if stock_data is not None and not stock_data.empty:
    user_question = st.text_area("Ask the AI about this stock data:", placeholder="e.g., Why is the trend falling?")

    if st.button("Ask AI", key="ai_btn") and user_question.strip():
        try:
            summary = stock_data["Close"].describe().to_string()
            prompt = (
                f"Here is some historical stock price data for {ticker_symbol}:\n"
                f"{summary}\n\n"
                f"User question: {user_question}"
            )

            response = client.chat.completions.create(
                model=deployment,
                messages=[
                    {"role": "system", "content": "You are a financial analyst AI assistant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7,
            )

            if response.choices and response.choices[0].message:
                answer = response.choices[0].message.content
                st.markdown("### 💬 AI's Response")
                st.write(answer)
            else:
                st.warning("AI response was empty. Please try again.")

        except Exception as e:
            st.error(f"AI Error: {e}")
            st.stop()  # Stops execution here to prevent app restart


