import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AtenderReservaService {

  private apiUrl = `${environment.apiUrl}/api/atender-reserva`;

  constructor(private http: HttpClient) {}

  listarReservas(idSucursal: number): Observable<any> {
    const params = new HttpParams()
      .set('id_sucursal', idSucursal.toString());

    return this.http.get<any>(
      this.apiUrl,
      { params }
    );
  }

  obtenerReserva(
    idReserva: number,
    idSucursal: number
  ): Observable<any> {

    const params = new HttpParams()
      .set('id_sucursal', idSucursal.toString());

    return this.http.get<any>(
      `${this.apiUrl}/${idReserva}`,
      { params }
    );
  }

  atenderReserva(
    idReserva: number,
    idSucursal: number
  ): Observable<any> {

    const params = new HttpParams()
      .set('id_sucursal', idSucursal.toString());

    return this.http.post<any>(
      `${this.apiUrl}/${idReserva}`,
      {},
      { params }
    );
  }
}