import { apiGetApps, apiRequest } from './requests'
export { apiGetApps, apiRequest }

export const paginateRecords = (records, currentPage, recordsPerPage) =>
  records.slice(currentPage * recordsPerPage, currentPage * recordsPerPage + recordsPerPage)
