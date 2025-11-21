import streamlit as st
st.title('나의 첫 웹앱 제작!')
st.write('찬환이의 바이브 코딩 Start! wow:)')
name = st.text_input('이름을 입력해주세요 : ')
menu = st.selectbox('좋아하는 음식을 선택해주세요:', ['망고빙수','아몬드봉봉'])
if st.button('인사말 생성') : 
  st.write(name+'님! 당신이 좋아하는 음식은 '+menu+'이군요?! 저도 좋아요!!')
