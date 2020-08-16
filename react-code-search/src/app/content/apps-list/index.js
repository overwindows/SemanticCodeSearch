import Header from './header'
import List from './list'
import NavMenu from './nav-menu'
import Pagination from './pagination'
import React, { useMemo, useState } from 'react'
import config from 'config'
import styled from 'styled-components'
import { paginateRecords } from 'utils'
// import { apiGetApps, apiRequest } from 'utils/requests'

const FlexContainer = styled.div`
  display: flex;
  flex-flow: row wrap;
  margin: 2rem auto;
  max-width: 1400px;
  text-align: center;
`

const MainSection = styled.section`
  padding: 1rem;
  flex: 1;
  order: 2;
  text-align: left;
  width: 100%;
`

const NoResultsMessage = ({ category, searchTerm }) => (
  <p>{`Can't find any ${category ? `${category.toLowerCase()} ` : ''}code matching "${searchTerm}"`}</p>
)

const AppsList = ({ apps }) => {
  const [activeCategory, setActiveCategory] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [page, setPage] = useState(0)
  const [searchRes, setSearchRes] = useState([])
  const [isSearch, setIsSearch] = useState(false)
  const [filteredApps, setfilteredApps] = useState([])

  // const filteredApps = useMemo(
  //   () =>
  //     (activeCategory ? searchRes.filter(app => app.categories.includes(activeCategory)) : searchRes)
  //       .filter(app => `${app.name} ${app.description}`.toLowerCase().includes(searchTerm.toLowerCase()))
  //       .sort((a, b) => a.subscriptionsPrice - b.subscriptionsPrice),
  //   [activeCategory, searchRes, searchTerm]
  // )
  React.useEffect(() => {
    // setfilteredApps(searchRes)
    // alert(activeCategory)
    // alert(searchRes)
    // const filteredCode = (activeCategory ? searchRes.filter(app => app.categories.includes(activeCategory)) : searchRes)
    //       .filter(app => `${app.name} ${app.description}`.toLowerCase().includes(searchTerm.toLowerCase()))
    //       .sort((a, b) => a.subscriptionsPrice - b.subscriptionsPrice)
    setfilteredApps((activeCategory ? searchRes.filter(app => app.categories.includes(activeCategory)) : searchRes).sort((a, b) => a.subscriptionsPrice - b.subscriptionsPrice))
  }, [setfilteredApps, searchRes, activeCategory]);

  return (
    <FlexContainer>
      <NavMenu
        activeCategory={activeCategory}
        //categories={categories}
        categories={[
          ...new Set(
            searchRes
              .map(searchRes => searchRes.categories)
              .flat()
              .sort()
          ),
        ]}
        setActiveCategory={setActiveCategory}
        setPage={setPage}
      />
      <MainSection>
        <Header searchTerm={searchTerm} setPage={setPage} setSearchTerm={setSearchTerm} setSearchRes={setSearchRes} setIsSearch={setIsSearch} />
        {
          // searchRes.length > 0 ? (
          //   <>
          //     <Pagination count={searchRes.length} page={page} setPage={setPage} />
          //     <List apps={paginateRecords(searchRes, page, config.paginationSize)} searchTerm={searchTerm} />
          //   </>
          //   ) : (isSearch &&
          //     <NoResultsMessage category={activeCategory} searchTerm={searchTerm} />
          //   )
        }
        {filteredApps.length > 0 ? (
          <>
            <Pagination count={filteredApps.length} page={page} setPage={setPage} />
            <List apps={paginateRecords(filteredApps, page, config.paginationSize)} searchTerm={searchTerm} />
          </>
        ) : (isSearch &&
          <NoResultsMessage category={activeCategory} searchTerm={searchTerm} />
          )}
      </MainSection>
    </FlexContainer>
  )
}

export default AppsList
