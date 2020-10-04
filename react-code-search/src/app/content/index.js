import AppsList from './apps-list'
import Error from './error'
import Loader from './loader'
import React, { useEffect, useState } from 'react'
import Prism from 'prismjs/prism';


const Content = () => {
  const [apps, setApps] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    //   ;(async () => {
    //     const { json, requestError } = await apiRequest(apiGetApps, [])
    //     if (requestError) {
    //       setError(requestError)
    //     } else {
    //       const appsWithSubscriptionsPrice = json.map(app => ({
    //         subscriptionsPrice: computeSubscriptionsPrice(app.subscriptions),
    //         ...app,
    //       }))
    //       setApps(appsWithSubscriptionsPrice)
    //     }
    //     setIsLoading(false)
    //   })()
    setTimeout(() => Prism.highlightAll(), 0)
  }, [])

  if (isLoading) return <Loader />

  if (error) return <Error error={error} />

  return <AppsList apps={apps} />
}

export default Content
