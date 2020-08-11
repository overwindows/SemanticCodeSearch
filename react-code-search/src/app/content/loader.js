import React from 'react'
import styled from 'styled-components'
import { Loader as LoaderIcon } from 'assets/icons'

const FlexContainer = styled.div`
  height: 100%;
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
  cursor: wait;
`

const StyledLoader = styled(LoaderIcon)`
  fill: ${({ theme }) => theme.primary};
  width: 6rem;

  @media (min-width: ${({ theme }) => theme.screens.mobile}px) {
    width: 8rem;
  }
`

const Loader = () => (
  <FlexContainer>
    <StyledLoader />
  </FlexContainer>
)

export default Loader
