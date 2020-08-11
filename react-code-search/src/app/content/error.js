import React from 'react'
import styled from 'styled-components'
import { Error as ErrorIcon } from 'assets/icons'

const FlexContainer = styled.div`
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  text-align: center;
`

const StyledErrorIcon = styled(ErrorIcon)`
  margin: 0 1rem;
  max-width: 32rem;
`

const Title = styled.h2`
  color: ${({ theme }) => theme.error};
  line-height: 1;
  margin: 2rem 0 1rem;
`

const Message = styled.p`
  font-size: 1.1rem;
  font-weight: 400;
`

const EmailLink = styled.a`
  text-decoration: underline;
`

const Error = ({ error }) => (
  <FlexContainer>
    <StyledErrorIcon />
    <Title>{'Ooops! Something went wrong.'}</Title>
    <Message>
      {`Looks like you ran into a ${error.type} error (code ${error.status}). Please try to reload the page, or `}
      <EmailLink href="#">{'click here'}</EmailLink>
      {' to contact our support.'}
    </Message>
  </FlexContainer>
)

export default Error
